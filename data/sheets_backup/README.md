# Google Sheets Data Backup

This folder contains CSV exports of all tabs from your Google Sheets database.

## 📊 Spreadsheet: `story-generator`

**Spreadsheet ID:** `1zLGboBMPUbcaHvz8gOJGxP6F8F0yTg19G8vlZTG1g60`

### Backed Up Sheets:

| Sheet Name | Description |
|------------|-------------|
| **channels** | Channel configuration and metadata |
| **trend_data** | Trending topics and themes |
| **source_scripts** | Viral story templates (83 rows) |
| **story_blueprints** | Story structure blueprints (83 rows) |
| **hook_patterns** | Viral hook patterns (83 rows) |
| **game_library** | Available gameplay clips (11 rows) |
| **music_library** | Background music tracks |
| **sfx_library** | Sound effects library (150 rows) |
| **metricool_analytics** | Metricool analytics data |
| **youtube_analytics** | YouTube analytics data |
| **channel_analytics** | Channel performance metrics |
| **blueprint_history** | Blueprint selection history |

## 🔄 How to Update Backups

These CSV files are **snapshots** of your Google Sheets data. They are not automatically synced.

To update them:
1. Re-run the backup script
2. Or manually export from Google Sheets and commit

## ⚠️ Important Notes

- **These are backups only** - Your Python code still reads from Google Sheets in real-time
- Keep your Google Sheets as the primary data source
- Use these CSVs for:
  - Version history
  - Disaster recovery
  - Analysis/inspection
  - Sharing with collaborators

## 🔗 Links

- [View Google Sheet](https://docs.google.com/spreadsheets/d/1zLGboBMPUbcaHvz8gOJGxP6F8F0yTg19G8vlZTG1g60/edit)
- [Main Repository](../../)

---

**Last updated:** 2025-11-24 03:05 UTC
