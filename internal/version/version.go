package version

import (
	"fmt"
	"net/url"
	"runtime/debug"
	"strings"
	"sync"

	"github.com/go-git/go-git/v6"
)

var (
	Version   = "dev"
	Commit    = ""
	Branch    = ""
	BuildDate = ""
	RepoURL   = ""
	CommitURL = ""

	gitInfoOnce sync.Once
)

// EnsureGitInfo populates git metadata (commit, branch, repo/commit URLs) if not already set.
func EnsureGitInfo() {
	gitInfoOnce.Do(initGitInfo)
}

func initGitInfo() {
	// Try reading from .git repository if present
	if r, err := git.PlainOpenWithOptions(".", &git.PlainOpenOptions{DetectDotGit: true}); err == nil {
		if head, err := r.Head(); err == nil {
			if Commit == "" || Commit == "unknown" {
				Commit = head.Hash().String()
			}
			if Branch == "" && head.Name().IsBranch() {
				Branch = head.Name().Short()
			}
		}

		if RepoURL == "" {
			if cfg, err := r.Config(); err == nil && cfg != nil {
				remoteName := ""
				if Branch != "" && cfg.Branches[Branch] != nil {
					remoteName = cfg.Branches[Branch].Remote
				}
				if remoteName == "" || cfg.Remotes[remoteName] == nil {
					if cfg.Remotes["fork"] != nil {
						remoteName = "fork"
					} else if cfg.Remotes["origin"] != nil {
						remoteName = "origin"
					}
				}
				if remoteName != "" && cfg.Remotes[remoteName] != nil && len(cfg.Remotes[remoteName].URLs) > 0 {
					RepoURL = NormalizeGitURL(cfg.Remotes[remoteName].URLs[0])
				}
			}
		}
	}

	// Fallback to runtime/debug build info if Commit still empty or unknown
	if Commit == "" || Commit == "unknown" {
		if bi, ok := debug.ReadBuildInfo(); ok {
			for _, s := range bi.Settings {
				if s.Key == "vcs.revision" && s.Value != "" {
					Commit = s.Value
					break
				}
			}
		}
	}

	if RepoURL == "" {
		RepoURL = "https://github.com/tronbyt/server"
	}

	if CommitURL == "" {
		if Branch != "" && Branch != "HEAD" {
			CommitURL = fmt.Sprintf("%s/tree/%s", RepoURL, Branch)
		} else if Commit != "" && Commit != "unknown" {
			CommitURL = fmt.Sprintf("%s/tree/%s", RepoURL, Commit)
		} else {
			CommitURL = RepoURL
		}
	}
}

// NormalizeGitURL converts git remote URLs (SSH, SCP-like, or HTTPS) into a standard HTTPS web URL.
func NormalizeGitURL(raw string) string {
	raw = strings.TrimSpace(raw)
	if raw == "" {
		return ""
	}
	// git@github.com:owner/repo.git
	if rem, ok := strings.CutPrefix(raw, "git@"); ok {
		parts := strings.SplitN(rem, ":", 2)
		if len(parts) == 2 {
			host := parts[0]
			path := strings.TrimSuffix(parts[1], ".git")
			return fmt.Sprintf("https://%s/%s", host, path)
		}
	}
	// ssh://git@github.com/owner/repo.git
	if rem, ok := strings.CutPrefix(raw, "ssh://"); ok {
		if idx := strings.Index(rem, "@"); idx != -1 {
			rem = rem[idx+1:]
		}
		parts := strings.SplitN(rem, "/", 2)
		if len(parts) == 2 {
			host := parts[0]
			path := strings.TrimSuffix(parts[1], ".git")
			return fmt.Sprintf("https://%s/%s", host, path)
		}
	}
	// https://github.com/owner/repo.git
	if u, err := url.Parse(raw); err == nil && u.Host != "" {
		u.Path = strings.TrimSuffix(u.Path, ".git")
		return fmt.Sprintf("%s://%s%s", u.Scheme, u.Host, u.Path)
	}
	return strings.TrimSuffix(raw, ".git")
}
