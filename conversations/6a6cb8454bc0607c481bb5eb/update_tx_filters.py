#!/usr/bin/env python3
"""Add advanced filtering and sorting to the Transactions page."""

TX_PATH = "/var/www/verdiscan/transactions/index.html"

with open(TX_PATH, "r") as f:
    html = f.read()

# 1. Add sort dropdown and block range filter to the controls
old_controls = '''    <div class="filter-toggle" onclick="toggleRemarks()">
      <div class="toggle-switch" id="remarkToggle"></div>
      <span>Exclude Remarks</span>
    </div>
    <button class="refresh-btn" id="refreshBtn" onclick="loadTransactions(true)">'''

new_controls = '''    <div class="filter-toggle" onclick="toggleRemarks()">
      <div class="toggle-switch" id="remarkToggle"></div>
      <span>Exclude Remarks</span>
    </div>
    <select class="filter-select" id="sortSelect" onchange="applyFilters()">
      <option value="block-desc">Sort: Block ↓</option>
      <option value="block-asc">Sort: Block ↑</option>
      <option value="value-desc">Sort: Value ↓</option>
      <option value="value-asc">Sort: Value ↑</option>
      <option value="fee-desc">Sort: Fee ↓</option>
      <option value="fee-asc">Sort: Fee ↑</option>
    </select>
    <input class="filter-select" id="blockRangeFrom" type="number" placeholder="Block ≥" style="width:90px" onchange="applyFilters()" />
    <input class="filter-select" id="blockRangeTo" type="number" placeholder="Block ≤" style="width:90px" onchange="applyFilters()" />
    <button class="refresh-btn" id="refreshBtn" onclick="loadTransactions(true)">'''

if 'sortSelect' not in html:
    html = html.replace(old_controls, new_controls)
    print("Added sort dropdown and block range filters")

# 2. Make column headers clickable for sorting
old_headers = '''          <tr>
            <th>EXTRINSIC HASH</th>
            <th>BLOCK</th>
            <th>TIME</th>
            <th>METHOD</th>
            <th>SIGNER</th>
            <th>VALUE (VRDX)</th>
            <th>FEE (VRDX)</th>
            <th>SECTION</th>
          </tr>'''

new_headers = '''          <tr>
            <th>EXTRINSIC HASH</th>
            <th style="cursor:pointer;user-select:none" onclick="setSort('block')">BLOCK <span id="sortBlock"></span></th>
            <th>TIME</th>
            <th>METHOD</th>
            <th>SIGNER</th>
            <th style="cursor:pointer;user-select:none" onclick="setSort('value')">VALUE (VRDX) <span id="sortValue"></span></th>
            <th style="cursor:pointer;user-select:none" onclick="setSort('fee')">FEE (VRDX) <span id="sortFee"></span></th>
            <th>SECTION</th>
          </tr>'''

if 'sortBlock' not in html:
    html = html.replace(old_headers, new_headers)
    print("Added sortable column headers")

# 3. Add sorting JavaScript
old_js = '''var excludeRemarks = false;
var ws = null;'''

new_js = '''var excludeRemarks = false;
var ws = null;
var currentSort = "block-desc";

function setSort(field) {
  var select = document.getElementById("sortSelect");
  var current = select.value;
  var parts = current.split("-");
  var newDir = parts[1] === "desc" ? "asc" : "desc";
  currentSort = field + "-" + newDir;
  select.value = currentSort;
  applyFilters();
}

function updateSortIndicators() {
  document.getElementById("sortBlock").textContent = "";
  document.getElementById("sortValue").textContent = "";
  document.getElementById("sortFee").textContent = "";
  var parts = currentSort.split("-");
  var arrow = parts[1] === "desc" ? "↓" : "↑";
  if (parts[0] === "block") document.getElementById("sortBlock").textContent = arrow;
  if (parts[0] === "value") document.getElementById("sortValue").textContent = arrow;
  if (parts[0] === "fee") document.getElementById("sortFee").textContent = arrow;
}'''

if 'setSort' not in html:
    html = html.replace(old_js, new_js)
    print("Added sorting JavaScript")

# 4. Update the applyFilters function to include sorting and block range
old_filter = '''  // Apply filters
  var searchQuery = document.getElementById("searchInput").value.toLowerCase().trim();
  var typeFilter = document.getElementById("typeFilter").value;
  var filtered = allTransactions.filter(function(tx) {
    if (excludeRemarks && tx.fullType === "system.remark") return false;
    if (searchQuery) {
      var matchStr = (tx.hash || "") + " " + (tx.block || "") + " " + (tx.method || "") + " " + (tx.signer || "") + " " + (tx.fullType || "");
      if (matchStr.toLowerCase().indexOf(searchQuery) === -1) return false;
    }
    if (typeFilter && tx.fullType !== typeFilter) return false;
    return true;
  });'''

new_filter = '''  // Apply filters
  var searchQuery = document.getElementById("searchInput").value.toLowerCase().trim();
  var typeFilter = document.getElementById("typeFilter").value;
  currentSort = document.getElementById("sortSelect").value;
  var blockFrom = parseInt(document.getElementById("blockRangeFrom").value) || 0;
  var blockTo = parseInt(document.getElementById("blockRangeTo").value) || 999999999;
  var filtered = allTransactions.filter(function(tx) {
    if (excludeRemarks && tx.fullType === "system.remark") return false;
    if (searchQuery) {
      var matchStr = (tx.hash || "") + " " + (tx.block || "") + " " + (tx.method || "") + " " + (tx.signer || "") + " " + (tx.fullType || "");
      if (matchStr.toLowerCase().indexOf(searchQuery) === -1) return false;
    }
    if (typeFilter && tx.fullType !== typeFilter) return false;
    if (tx.block < blockFrom || tx.block > blockTo) return false;
    return true;
  });

  // Apply sorting
  var parts = currentSort.split("-");
  var sortField = parts[0];
  var sortDir = parts[1] === "desc" ? -1 : 1;
  filtered.sort(function(a, b) {
    var va = parseFloat(a[sortField]) || 0;
    var vb = parseFloat(b[sortField]) || 0;
    return (va - vb) * sortDir;
  });
  updateSortIndicators();'''

if 'blockFrom' not in html:
    html = html.replace(old_filter, new_filter)
    print("Updated filter function with sorting and block range")

# 5. Add CSS for block range inputs to look good on mobile
old_mobile_css = '''  .search-box{min-width:0}'''

new_mobile_css = '''  .search-box{min-width:0}
  .controls-inner{flex-wrap:wrap;gap:6px}
  .filter-select{font-size:11px}
  #blockRangeFrom,#blockRangeTo{width:70px !important}'''

if 'controls-inner{flex-wrap' not in html:
    html = html.replace(old_mobile_css, new_mobile_css)
    print("Added mobile CSS for filters")

with open(TX_PATH, "w") as f:
    f.write(html)
print(f"File saved: {len(html)} bytes")
