package server

// Admin preference for contacting Niblet Cloud (install counts and community stats).

import (
	"context"
	"errors"
	"log/slog"
	"strconv"
)

const settingNibletCloudEnabled = "niblet_cloud_enabled"

// isNibletCloudConfigured reports whether NIBLET_CLOUD_URL is set.
func (s *Server) isNibletCloudConfigured() bool {
	return s.Config.NibletCloudURL != ""
}

// isNibletCloudEnabled reports whether this server may contact Niblet Cloud.
func (s *Server) isNibletCloudEnabled() bool {
	return s.isNibletCloudConfigured() && s.nibletCloudEnabled.Load()
}

func (s *Server) loadNibletCloudEnabled() {
	enabled := s.isNibletCloudConfigured()
	if val, err := s.getSetting(settingNibletCloudEnabled); err == nil && val != "" {
		enabled = val == "true"
	}
	s.nibletCloudEnabled.Store(enabled && s.isNibletCloudConfigured())
}

// setNibletCloudEnabled saves an admin's choice and stops or resumes Niblet traffic.
func (s *Server) setNibletCloudEnabled(enabled bool) error {
	if !s.isNibletCloudConfigured() {
		return errors.New("niblet cloud is not configured")
	}
	s.nibletCloudPreferenceMutex.Lock()
	defer s.nibletCloudPreferenceMutex.Unlock()

	wasEnabled := s.nibletCloudEnabled.Load()
	if wasEnabled && !enabled {
		consent, _ := s.getSetting(settingUsageSharing)
		token, _ := s.getSetting(settingUsageToken)
		if consent == "true" || token != "" {
			if err := s.setSetting(settingUsageSharing, "false"); err != nil {
				return err
			}
			s.usageForce.Store(true)
			if err := s.syncUsage(context.Background()); err != nil {
				slog.Warn("App usage sharing deferred", "error", err)
			}
		}
	}

	if err := s.setSetting(settingNibletCloudEnabled, strconv.FormatBool(enabled)); err != nil {
		return err
	}
	s.nibletCloudEnabled.Store(enabled)
	if wasEnabled && !enabled {
		s.setNibletCounts(map[string]int64{})
	}

	if !wasEnabled && enabled {
		s.usageSyncs.Go(func() {
			if err := s.syncNiblet(context.Background()); err != nil {
				slog.Warn("Niblet install counts sync deferred", "error", err)
			}
		})
	}
	return nil
}
