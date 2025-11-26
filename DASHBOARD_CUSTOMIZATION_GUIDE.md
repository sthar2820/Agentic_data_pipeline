# Dashboard Customization Guide

## Overview

The Analytics Dashboard now includes **full customization capabilities**, allowing you to add, remove, and toggle visualizations as needed for your specific analysis requirements.

---

## New Features

### 1. ⚙️ Customize Dashboard Button

**Location:** Top-right of Analytics Dashboard (next to "Ask AI" button)

**Purpose:** Opens the dashboard customization panel where you can:
- Toggle visibility of dashboard sections
- Add custom visualizations
- Remove custom visualizations

---

### 2. Toggle Dashboard Sections

**Available Sections to Toggle:**

| Section | Description | Default State |
|---------|-------------|---------------|
| 📋 Executive Summary | Automated insights and key findings | ON |
| 🎯 Data Health Scorecard | Completeness, uniqueness, consistency metrics | ON |
| 📈 Business Metrics | Primary metric analysis and category performance | ON |
| 🔗 Feature Relationships | Correlation matrix and top correlations | ON |
| 📈 Statistical Summary | Descriptive statistics and quality metrics | ON |
| 📊 Interactive Explorer | Dynamic scatter plot builder | ON |
| 🎨 Pipeline Insights | Auto-generated visualizations | ON |

**How to Use:**
1. Click "⚙️ Customize Dashboard" button
2. Check/uncheck sections to show/hide them
3. Changes apply immediately
4. Sections remain hidden/visible across dashboard refreshes

---

### 3. Add Custom Visualizations

**Location:** Customization Panel → "Add Custom Visualization" section

**Supported Chart Types:**
- **Scatter** - Relationship between two numeric variables
- **Line** - Trends over continuous data
- **Bar** - Comparisons across categories
- **Histogram** - Distribution of single numeric variable
- **Box** - Statistical distribution with quartiles
- **Violin** - Distribution shape visualization
- **Heatmap** - Correlation matrix of all numeric features
- **Pie** - Proportional composition of categories

**How to Add a Visualization:**

1. **Select Chart Type**
   - Choose from dropdown: scatter, line, bar, histogram, box, violin, heatmap, pie

2. **Configure Axes**
   - **X-Axis:** Select column for horizontal axis
     - For scatter/line/box/violin: numeric columns only
     - For bar/pie: numeric or categorical columns
     - For histogram/heatmap: automatic

   - **Y-Axis:** (if applicable) Select column for vertical axis
     - Available for: scatter, line, bar, box, violin
     - Not needed for: histogram, pie, heatmap

3. **Add Color Grouping** (optional)
   - Available for: scatter, line, bar
   - Select categorical column to group data by color
   - Choose "None" for single-color visualization

4. **Click "➕ Add Visualization"**
   - Visualization appears immediately in "Custom Visualizations" section
   - Positioned above all dashboard sections
   - Displayed in 2-column grid layout

---

### 4. Remove Custom Visualizations

**How to Remove:**
1. Scroll to "Custom Visualizations" list in customization panel
2. Each visualization shows:
   - Position number (1, 2, 3, ...)
   - Title (e.g., "Scatter: price vs discount")
   - 🗑️ Remove button
3. Click "🗑️ Remove" button next to visualization
4. Visualization removed immediately from dashboard

---

## Usage Examples

### Example 1: Focus on Business Metrics Only

**Scenario:** You only want to see business-focused visualizations

**Steps:**
1. Click "⚙️ Customize Dashboard"
2. Uncheck all sections except:
   - ✓ Business Metrics
   - ✓ Feature Relationships
3. Dashboard now shows only business metrics and correlations

---

### Example 2: Add Price vs Discount Scatter Plot

**Scenario:** Analyze relationship between price and discount

**Steps:**
1. Click "⚙️ Customize Dashboard"
2. In "Add Custom Visualization" section:
   - Chart Type: **scatter**
   - X-Axis: **price**
   - Y-Axis: **discount**
   - Color By: **selling_proposition** (optional)
3. Click "➕ Add Visualization"
4. Scatter plot appears at top of dashboard
5. Interactive features: zoom, pan, hover for details

---

### Example 3: Create Multiple Distribution Views

**Scenario:** Compare distributions of different numeric columns

**Steps:**
1. Add Histogram #1:
   - Chart Type: **histogram**
   - X-Axis: **price**
   - Click "➕ Add Visualization"

2. Add Histogram #2:
   - Chart Type: **histogram**
   - X-Axis: **discount**
   - Click "➕ Add Visualization"

3. Add Box Plot:
   - Chart Type: **box**
   - X-Axis: **selling_proposition**
   - Y-Axis: **price**
   - Click "➕ Add Visualization"

4. Result: 3 custom visualizations in grid layout

---

### Example 4: Category Analysis Setup

**Scenario:** Deep dive into categorical data

**Steps:**
1. Toggle OFF:
   - Executive Summary
   - Statistical Summary
2. Add visualizations:
   - Pie chart of top categories
   - Bar chart with color grouping
   - Box plot by category
3. Keep ON:
   - Categorical Analysis tab (in Statistical Summary section)

---

## Custom Visualization Gallery

### Scatter Plot
```
Chart Type: scatter
X-Axis: price
Y-Axis: discount
Color By: category
```
**Use Case:** Identify price-discount patterns across categories

### Line Chart
```
Chart Type: line
X-Axis: date (if available)
Y-Axis: price
Color By: category
```
**Use Case:** Trend analysis over time

### Histogram
```
Chart Type: histogram
X-Axis: price
```
**Use Case:** Understand price distribution shape

### Box Plot
```
Chart Type: box
X-Axis: category
Y-Axis: price
```
**Use Case:** Compare distributions across categories

### Violin Plot
```
Chart Type: violin
X-Axis: category
Y-Axis: discount
```
**Use Case:** See distribution shape by category

### Heatmap
```
Chart Type: heatmap
(No axis selection needed)
```
**Use Case:** Full correlation matrix of all numeric features

### Pie Chart
```
Chart Type: pie
Column: category
```
**Use Case:** Proportional breakdown of categories

---

## Pro Tips

### Tip 1: Start with Defaults, Then Customize
- Run pipeline first to see all default visualizations
- Identify what you need
- Use customization to focus on relevant sections

### Tip 2: Create Analysis-Specific Dashboards
- **Data Quality Focus:** Keep only Health Scorecard + Executive Summary
- **Business Analysis:** Keep only Business Metrics + Custom visualizations
- **Statistical Analysis:** Keep only Statistical Summary + Feature Relationships

### Tip 3: Use Custom Visualizations for Exploration
- Add scatter plots to explore relationships
- Add box plots to compare distributions
- Add histograms for detailed distribution analysis
- Remove when done exploring

### Tip 4: Combine with AI Chatbot
1. Add custom visualizations for initial exploration
2. Use "💬 Ask AI" for additional ad-hoc visualizations
3. Keep successful visualizations, remove others
4. AI chatbot provides temporary visualizations in modal

### Tip 5: Session Persistence
- Toggle settings persist during session
- Custom visualizations remain until removed
- Refresh page to reset to defaults
- Settings reset between different datasets

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Toggle customization panel | Click "⚙️ Customize Dashboard" |
| Add visualization | Click "➕ Add Visualization" |
| Remove visualization | Click "🗑️ Remove" button |
| Close customization | Click "⚙️ Customize Dashboard" again |

---

## Technical Details

### Session State Management
- `st.session_state.show_sections` - Dictionary tracking section visibility
- `st.session_state.custom_visualizations` - List of custom viz configurations
- `st.session_state.show_customize` - Boolean for panel visibility

### Visualization Configuration Format
```python
{
    'type': 'scatter',          # Chart type
    'x': 'price',               # X-axis column
    'y': 'discount',            # Y-axis column (optional)
    'color': 'category',        # Color grouping (optional)
    'title': 'Scatter: price vs discount'  # Display title
}
```

### Conditional Rendering
Each dashboard section is wrapped in:
```python
if st.session_state.show_sections['section_name']:
    # Section content here
```

---

## Limitations

1. **Custom Visualizations**
   - Limited to 8 chart types
   - Cannot customize colors/themes (uses plotly_white)
   - Cannot add annotations or trend lines

2. **Section Toggles**
   - Cannot reorder sections
   - Cannot create custom sections
   - Changes reset on page refresh

3. **Performance**
   - Many custom visualizations may slow rendering
   - Recommendation: Keep custom viz count under 6
   - Complex correlations (heatmap) may be slow on large datasets

---

## Troubleshooting

### Issue: Customization panel not appearing
**Solution:** Ensure data has been processed first. Button only appears when `processed_data` is available.

### Issue: Visualization not rendering
**Solution:**
- Check that selected columns exist in dataset
- Verify column types match chart requirements
- Try different chart type

### Issue: Color grouping not working
**Solution:**
- Ensure selected color column is categorical
- Try different categorical column
- Set color to "None" if issues persist

### Issue: Changes not saving
**Solution:**
- Changes persist during session only
- Refresh page to reset
- Re-apply customizations after page refresh

---

## Best Practices

### 1. Progressive Disclosure
- Start with all sections visible
- Hide sections as you narrow focus
- Re-enable sections for comprehensive view

### 2. Purpose-Driven Customization
- Quality Check: Health + Summary
- Business Review: Business Metrics + Custom viz
- Statistical Analysis: Stats + Relationships
- Exploration: Everything + Custom viz

### 3. Visualization Hygiene
- Remove unused custom visualizations
- Keep dashboard clean and focused
- Use descriptive titles for custom viz

### 4. Performance Optimization
- Limit custom visualizations to 4-6
- Disable heavy sections (heatmap) when not needed
- Use sampling for large datasets

---

## Future Enhancements (Planned)

1. **Save Dashboard Layouts** - Save and load custom configurations
2. **Export Custom Views** - Export specific section combinations
3. **Advanced Customization** - Colors, themes, annotations
4. **Section Reordering** - Drag-and-drop section arrangement
5. **Templates** - Pre-configured layouts for common use cases

---

## Summary

The Dashboard Customization feature provides:

✅ **Full Control** - Show/hide any dashboard section
✅ **Custom Visualizations** - Add 8 chart types on demand
✅ **Easy Management** - One-click add/remove
✅ **Flexible Layouts** - Focus on what matters
✅ **Session Persistence** - Changes remain during session
✅ **No Coding Required** - Point-and-click interface

**Access:** Click "⚙️ Customize Dashboard" in Analytics Dashboard

**Combine with:** "💬 Ask AI" for maximum flexibility

---

**Powered by Agentic Data Pipeline** 🤖
