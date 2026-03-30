# ll-KNOWRAG Workflow (Autopilot)

- **Mode**: autopilot
- **Cycle**: 3
- **Current Step**: Done

## Acceptance Criteria (Slice 7.6)
- [x] Link extraction in CrawlerManager (internal only, filtered).
- [x] Recursive crawl loop in CrawlingService.
- [x] max_depth enforcement.
- [x] max_pages enforcement across all modes.
- [x] Visited URL tracking to prevent loops.
- [x] Existing modes (Single, Sitemap, Auto) remain stable.
- [x] Verified via tests.

## Acceptance Criteria (Slice 7.7)
- [x] llms.txt parsing for actionable URLs.
- [x] Task expansion in DiscoveryAuto mode.
- [x] max_pages limit applies to expanded tasks.
- [x] Verified via tests.
