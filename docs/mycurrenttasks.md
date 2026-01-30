# Current Tasks - Bheem DataViz

## Backlog 📋

### 1. Export Chart as Image
**Status:** ✅ Completed
- Added download button to charts
- Uses ECharts getDataURL() method with 2x pixel ratio for high quality
- Available in:
  - Chart Builder (main chart display)
  - Saved chart viewing page
  - Dashboard chart cards (hover to see download button)

### 2. Better Data Tables
**Status:** ✅ Completed
- Sortable columns (click header to sort asc/desc with arrow indicator)
- Pagination (10/25/50/100 rows per page, Prev/Next + page numbers)
- Proper formatting (numbers with commas, large numbers as M/K, dates formatted)
- Row counter showing "Showing X-Y of Z rows"

### 3. Dashboard Filters/Slicers
**Status:** Pending (removed - not needed now)
- Add dropdown filters at dashboard level
- Filter all charts simultaneously

### 4. Chart Tooltips Enhancement
**Status:** Pending
- Better tooltips with more context

### 5. Drill-down to Data
**Status:** Pending
- Click chart element to see underlying data

---

## Completed ✅

- [x] **Drag & Drop Widget Panel** - Side panel with tabs for Charts/KPIs/Models/Transforms, drag items to dashboard
- [x] **Dashboard Chart Card Redesign** - Full-bleed charts with overlay titles, matches KPI card size
- [x] **Better Data Tables** - Sortable columns, pagination, number/date formatting
- [x] **Export Chart as Image** - Download charts as PNG with one click
- [x] **More Chart Types** - Added Horizontal Bar, Scatter, Gauge, Funnel, Radar charts
- [x] Custom chart naming when saving
- [x] Delete charts from dashboard
- [x] Generate all chart types (removed 10-category limit)
- [x] Better chart selection UI with type badges
- [x] Chart preview in saved charts list
