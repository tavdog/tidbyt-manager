package version

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNormalizeGitURL(t *testing.T) {
	tests := []struct {
		input string
		want  string
	}{
		{
			input: "git@github.com:brombomb/tronbyt-server.git",
			want:  "https://github.com/brombomb/tronbyt-server",
		},
		{
			input: "git@github.com:brombomb/tronbyt-server",
			want:  "https://github.com/brombomb/tronbyt-server",
		},
		{
			input: "ssh://git@github.com/brombomb/tronbyt-server.git",
			want:  "https://github.com/brombomb/tronbyt-server",
		},
		{
			input: "https://github.com/brombomb/tronbyt-server.git",
			want:  "https://github.com/brombomb/tronbyt-server",
		},
		{
			input: "https://github.com/brombomb/tronbyt-server",
			want:  "https://github.com/brombomb/tronbyt-server",
		},
		{
			input: "",
			want:  "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			got := NormalizeGitURL(tt.input)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestInitGitInfo(t *testing.T) {
	EnsureGitInfo()

	assert.NotEmpty(t, Commit)
	assert.NotEqual(t, "unknown", Commit)
	assert.NotEmpty(t, RepoURL)
	assert.NotEmpty(t, CommitURL)
	assert.Contains(t, CommitURL, RepoURL)
}
