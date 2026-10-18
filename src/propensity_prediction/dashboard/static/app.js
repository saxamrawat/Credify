"use strict";

const INTEGER_FIELDS = new Set([
  "ID", "SEX", "EDUCATION", "MARRIAGE",
  "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
]);
const NON_NEGATIVE_FIELDS = new Set([
  "LIMIT_BAL", "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6",
]);
const INTEGER_RANGES = {
  SEX: [1, 2],
  EDUCATION: [0, 4],
  MARRIAGE: [0, 3],
};
const CATEGORICAL_FIELDS = new Set([
  "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
]);
const DASHBOARD_FIELDS = new Set(["SEX", "EDUCATION", "MARRIAGE"]);
const PAGE_SIZE = 50;

const elements = {
  form: document.querySelector("#analysis-form"),
  file: document.querySelector("#portfolio-file"),
  fileName: document.querySelector("#file-name"),
  fileHint: document.querySelector("#file-hint"),
  capacity: document.querySelector("#review-capacity"),
  runButton: document.querySelector("#run-analysis"),
  formMessage: document.querySelector("#form-message"),
  status: document.querySelector("#service-status"),
  healthCheck: document.querySelector("#health-check"),
  emptyState: document.querySelector("#empty-state"),
  results: document.querySelector("#results-section"),
  metrics: document.querySelector("#metric-grid"),
  riskBands: document.querySelector("#risk-band-chart"),
  riskReference: document.querySelector("#risk-band-reference"),
  capacityRing: document.querySelector("#capacity-ring"),
  capacityPercent: document.querySelector("#capacity-percent"),
  capacityLegend: document.querySelector("#capacity-legend"),
  capacityFootnote: document.querySelector("#capacity-footnote"),
  portfolioCount: document.querySelector("#portfolio-count"),
  analysisMeta: document.querySelector("#analysis-meta"),
  analysisMetaText: document.querySelector("#analysis-meta-text"),
  exploreView: document.querySelector("#explore-view"),
  queueView: document.querySelector("#queue-view"),
  viewLinks: [...document.querySelectorAll("[data-view]")],
  exploreCount: document.querySelector("#explore-count"),
  customerIdFilter: document.querySelector("#filter-customer-id"),
  scoreMinFilter: document.querySelector("#filter-score-min"),
  scoreMaxFilter: document.querySelector("#filter-score-max"),
  riskBandFilter: document.querySelector("#filter-risk-band"),
  reviewStatusFilter: document.querySelector("#filter-review-status"),
  featureFilter: document.querySelector("#filter-feature"),
  featureValueControl: document.querySelector("#feature-value-control"),
  resetFilters: document.querySelector("#reset-filters"),
  filterMessage: document.querySelector("#filter-message"),
  groupByField: document.querySelector("#group-by-field"),
  scoreDistribution: document.querySelector("#score-distribution"),
  groupSummaryBody: document.querySelector("#group-summary-body"),
  groupTableNote: document.querySelector("#group-table-note"),
  customerResultsBody: document.querySelector("#customer-results-body"),
  pageCount: document.querySelector("#page-count"),
  pageStatus: document.querySelector("#page-status"),
  previousPage: document.querySelector("#previous-page"),
  nextPage: document.querySelector("#next-page"),
  queuePopulationCount: document.querySelector("#queue-population-count"),
  queueMetricGrid: document.querySelector("#queue-metric-grid"),
  queueReasonsBody: document.querySelector("#queue-reasons-body"),
  selectedQueueBody: document.querySelector("#selected-queue-body"),
  queuePageCount: document.querySelector("#queue-page-count"),
  queuePageStatus: document.querySelector("#queue-page-status"),
  queuePreviousPage: document.querySelector("#queue-previous-page"),
  queueNextPage: document.querySelector("#queue-next-page"),
  selectionProfileGroups: document.querySelector("#selection-profile-groups"),
  featureInsightsView: document.querySelector("#feature-insights-view"),
  featureInsightsCount: document.querySelector("#feature-insights-count"),
  repaymentStatusChart: document.querySelector("#repayment-status-chart"),
  monthlyBillSummary: document.querySelector("#monthly-bill-summary"),
  monthlyPaymentSummary: document.querySelector("#monthly-payment-summary"),
  importanceMethodDescription: document.querySelector("#importance-method-description"),
  modelImportanceChart: document.querySelector("#model-importance-chart"),
  importanceReferenceNote: document.querySelector("#importance-reference-note"),
  customerDialog: document.querySelector("#customer-dialog"),
  customerDialogTitle: document.querySelector("#customer-dialog-title"),
  customerDetailContent: document.querySelector("#customer-detail-content"),
  closeCustomerDialog: document.querySelector("#close-customer-dialog"),
  exportFiltered: document.querySelector("#export-filtered"),
  exportRanking: document.querySelector("#export-ranking"),
  exportQueue: document.querySelector("#export-queue"),
  analystForm: document.querySelector("#analyst-form"),
  analystQuestion: document.querySelector("#analyst-question"),
  analystSubmit: document.querySelector("#analyst-submit"),
  analystAnswer: document.querySelector("#analyst-answer"),
  analystState: document.querySelector("#analyst-state"),
  analystClaims: document.querySelector("#analyst-claims"),
  analystCitations: document.querySelector("#analyst-citations"),
  analystDisclaimer: document.querySelector("#analyst-disclaimer"),
};

let dashboardConfig = null;
let selectedFile = null;
let currentPortfolio = [];
let currentInputRows = [];
let currentResult = null;
let filteredPortfolio = [];
let currentPage = 0;
let queuePage = 0;
let activeView = "overview";
const quartileBoundaryCache = new Map();

const percentFormatter = new Intl.NumberFormat(undefined, {
  style: "percent",
  maximumFractionDigits: 1,
});
const numberFormatter = new Intl.NumberFormat(undefined, {
  maximumFractionDigits: 0,
});

function showMessage(message, kind = "error") {
  elements.formMessage.textContent = message;
  elements.formMessage.hidden = false;
  elements.formMessage.classList.toggle("is-success", kind === "success");
}

function clearMessage() {
  elements.formMessage.textContent = "";
  elements.formMessage.hidden = true;
  elements.formMessage.classList.remove("is-success");
}

function setServiceStatus(ready, message) {
  elements.status.classList.toggle("is-ready", ready);
  elements.status.classList.toggle("is-error", !ready);
  elements.status.lastChild.textContent = ` ${message}`;
}

function parseCsv(text) {
  const source = text.replace(/^\uFEFF/, "");
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;
  let afterQuote = false;

  for (let index = 0; index < source.length; index += 1) {
    const character = source[index];
    const next = source[index + 1];

    if (inQuotes) {
      if (character === '"' && next === '"') {
        field += '"';
        index += 1;
      } else if (character === '"') {
        inQuotes = false;
        afterQuote = true;
      } else {
        field += character;
      }
      continue;
    }

    if (afterQuote) {
      if (character === ",") {
        row.push(field);
        field = "";
        afterQuote = false;
      } else if (character === "\n" || character === "\r") {
        row.push(field);
        appendCsvRow(rows, row);
        row = [];
        field = "";
        afterQuote = false;
        if (character === "\r" && next === "\n") index += 1;
      } else if (character === " " || character === "\t") {
        // Ignore whitespace between a closing quote and its delimiter.
      } else {
        throw new Error("The CSV has invalid characters after a quoted value.");
      }
      continue;
    }

    if (character === '"') {
      if (field.length > 0) {
        throw new Error("The CSV contains a quote inside an unquoted value.");
      }
      inQuotes = true;
    } else if (character === ",") {
      row.push(field);
      field = "";
    } else if (character === "\n" || character === "\r") {
      row.push(field);
      appendCsvRow(rows, row);
      row = [];
      field = "";
      if (character === "\r" && next === "\n") index += 1;
    } else {
      field += character;
    }
  }

  if (inQuotes) throw new Error("The CSV contains an unclosed quoted value.");
  if (field.length > 0 || row.length > 0 || afterQuote) {
    row.push(field);
    appendCsvRow(rows, row);
  }
  return rows;
}

function appendCsvRow(rows, row) {
  if (row.length === 1 && row[0] === "") return;
  rows.push(row);
}

function parseNumeric(value, column, csvRowNumber) {
  const trimmed = value.trim();
  const decimalPattern = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/;
  if (!decimalPattern.test(trimmed)) {
    throw new Error(`${column} must contain numeric values. Check CSV row ${csvRowNumber}.`);
  }
  const number = Number(trimmed);
  if (!Number.isFinite(number)) {
    throw new Error(`${column} must contain finite numeric values. Check CSV row ${csvRowNumber}.`);
  }
  if (INTEGER_FIELDS.has(column) && !Number.isInteger(number)) {
    throw new Error(`${column} must contain integer values. Check CSV row ${csvRowNumber}.`);
  }
  if (column === "ID" && !Number.isSafeInteger(number)) {
    throw new Error(`ID must be a safely representable integer. Check CSV row ${csvRowNumber}.`);
  }
  if (NON_NEGATIVE_FIELDS.has(column) && number < 0) {
    throw new Error(`${column} must be non-negative. Check CSV row ${csvRowNumber}.`);
  }
  if (Object.hasOwn(INTEGER_RANGES, column)) {
    const [minimum, maximum] = INTEGER_RANGES[column];
    if (number < minimum || number > maximum) {
      throw new Error(`${column} must use values from ${minimum} through ${maximum}. Check CSV row ${csvRowNumber}.`);
    }
  }
  return number;
}

function validateCsvRows(rows) {
  if (!rows.length) throw new Error("The CSV is empty.");
  const [headers, ...dataRows] = rows;
  if (!headers.length || headers.every((header) => header === "")) {
    throw new Error("The CSV must include a header row.");
  }
  if (new Set(headers).size !== headers.length) {
    throw new Error("The CSV contains duplicate column names.");
  }
  if (headers.includes("DEFAULT")) {
    throw new Error("DEFAULT is a historical outcome, not an input for prediction. Upload a prediction-time file without this column.");
  }

  const required = dashboardConfig.required_columns;
  const missing = required.filter((column) => !headers.includes(column));
  const extra = headers.filter((column) => !required.includes(column));
  if (missing.length || extra.length) {
    const problems = [];
    if (missing.length) problems.push(`Missing required columns: ${missing.join(", ")}.`);
    if (extra.length) problems.push(`Unrecognized columns: ${extra.join(", ")}.`);
    throw new Error(problems.join(" "));
  }
  if (!dataRows.length) throw new Error("The CSV must contain at least one customer row.");
  if (dataRows.length > dashboardConfig.max_customer_rows) {
    throw new Error(`The CSV contains ${numberFormatter.format(dataRows.length)} customer rows; the maximum is ${numberFormatter.format(dashboardConfig.max_customer_rows)}. Split the portfolio into smaller files.`);
  }

  const seenIds = new Set();
  return dataRows.map((values, rowIndex) => {
    const csvRowNumber = rowIndex + 2;
    if (values.length !== headers.length) {
      throw new Error(`CSV row ${csvRowNumber} has ${values.length} values; expected ${headers.length}.`);
    }
    const sourceRow = Object.fromEntries(headers.map((header, index) => [header, values[index]]));
    const customer = {};
    for (const column of required) {
      const value = sourceRow[column];
      if (value === undefined || value.trim() === "") {
        throw new Error(`${column} cannot be blank. Check CSV row ${csvRowNumber}.`);
      }
      customer[column] = parseNumeric(value, column, csvRowNumber);
    }
    if (seenIds.has(customer.ID)) {
      throw new Error(`ID values must be unique. Duplicate ID ${customer.ID} appears in CSV row ${csvRowNumber}.`);
    }
    seenIds.add(customer.ID);
    return customer;
  });
}

function formatCount(value) {
  return numberFormatter.format(value);
}

function csvCell(value) {
  let text = String(value ?? "");
  if (typeof value !== "number" && /^[\s]*[=+@\-]/.test(text)) text = `'${text}`;
  return `"${text.replaceAll('"', '""')}"`;
}

function downloadCsv(filename, rows, metadata) {
  const metadataColumns = metadata.map(([key]) => key);
  const dataColumns = rows.length ? Object.keys(rows[0]) : [...dashboardConfig.required_columns,
    "predicted_default_probability", "risk_rank", "risk_band", "selected_for_review", "reason_code", "reason"];
  const columns = [...metadataColumns, ...dataColumns];
  const metadataValues = Object.fromEntries(metadata);
  const csv = [
    columns.map(csvCell).join(","),
    ...rows.map((row) => columns.map((column) => csvCell(
      Object.hasOwn(metadataValues, column) ? metadataValues[column] : row[column],
    )).join(",")),
  ].join("\r\n");
  const url = URL.createObjectURL(new Blob([`\uFEFF${csv}`], { type: "text/csv;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function exportRows(rows, filename, scope) {
  const fields = [...dashboardConfig.required_columns];
  const exports = rows.map((record) => {
    const input = Object.fromEntries(fields.map((field) => [field, record[field]]));
    return {
      ...input,
      predicted_default_probability: record.predicted_default_probability,
      risk_rank: record.risk_rank,
      risk_band: getRiskBand(record),
      selected_for_review: record.selected_for_review,
      reason_code: record.reason_code,
      reason: record.reason,
    };
  });
  downloadCsv(filename, exports, [
    ["Export scope", scope],
    ["Generated at", new Date().toISOString()],
    ["Portfolio size", currentPortfolio.length],
    ["Review capacity", currentResult.capacity.requested_review_count],
    ["Historical outcome fields included", "No"],
  ]);
}

async function showCustomerDetail(record) {
  elements.customerDialogTitle.textContent = `Customer ${record.customer_id}`;
  elements.customerDetailContent.replaceChildren(Object.assign(document.createElement("p"), { textContent: "Loading model explanation…" }));
  elements.customerDialog.showModal();
  const fieldNames = dashboardConfig.required_columns;
  const input = Object.fromEntries(fieldNames.map((field) => [field, record[field]]));
  try {
  const response = await fetch("/v1/customer-explanation", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(input),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload?.error?.message || "Could not load this customer explanation.");

  const profileHeading = document.createElement("h3");
  profileHeading.textContent = "Prediction-time inputs";
  const profile = document.createElement("dl");
  profile.className = "detail-profile";
  fieldNames.forEach((field) => {
    const term = document.createElement("dt"); term.textContent = field;
    const value = document.createElement("dd"); value.textContent = String(record[field]);
    profile.append(term, value);
  });
  const explanationHeading = document.createElement("h3"); explanationHeading.textContent = "Grouped model explanation";
  const intro = document.createElement("p");
  intro.textContent = `Model estimate ${formatPercent(payload.estimated_default_probability)}; reference-sample mean ${formatPercent(payload.reference_probability)}; difference ${payload.difference_from_reference >= 0 ? "+" : ""}${(payload.difference_from_reference * 100).toFixed(1)} percentage points.`;
  const contributionList = document.createElement("ul");
  payload.contributions.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = `${item.feature_group.replaceAll("_", " ")}: ${item.contribution >= 0 ? "+" : ""}${(item.contribution * 100).toFixed(2)} percentage points (${item.direction})`;
    contributionList.append(li);
  });
  const caveat = document.createElement("p"); caveat.className = "detail-caveat";
  caveat.textContent = `${payload.method}; background sample of ${payload.background_size}. ${payload.limitations} Queue rank: ${record.risk_rank}. ${record.selected_for_review ? "Selected for review" : "Not selected"}: ${record.reason}`;
  elements.customerDetailContent.replaceChildren(profileHeading, profile, explanationHeading, intro, contributionList, caveat);
  } catch (error) {
    const message = document.createElement("p");
    message.setAttribute("role", "alert");
    message.textContent = error.message || "Could not load this customer explanation.";
    elements.customerDetailContent.replaceChildren(message);
  }
}

function formatPercent(value) {
  return percentFormatter.format(value);
}

function formatProfileNumber(value) {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 1 }).format(value);
}

const PROFILE_MEASURES = [
  { label: "Predicted risk", read: (row) => row.predicted_default_probability, format: formatPercent },
  { label: "Credit limit", read: (row) => row.LIMIT_BAL, format: formatProfileNumber },
  { label: "Age (years)", read: (row) => row.AGE, format: formatProfileNumber },
  {
    label: "Average bill amount",
    read: (row) => meanOfFields(row, ["BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6"]),
    format: formatProfileNumber,
  },
  {
    label: "Average payment amount",
    read: (row) => meanOfFields(row, ["PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"]),
    format: formatProfileNumber,
  },
];

const MONTHLY_FEATURES = [
  { month: "April 2005", status: "PAY_6", bill: "BILL_AMT6", payment: "PAY_AMT6" },
  { month: "May 2005", status: "PAY_5", bill: "BILL_AMT5", payment: "PAY_AMT5" },
  { month: "June 2005", status: "PAY_4", bill: "BILL_AMT4", payment: "PAY_AMT4" },
  { month: "July 2005", status: "PAY_3", bill: "BILL_AMT3", payment: "PAY_AMT3" },
  { month: "August 2005", status: "PAY_2", bill: "BILL_AMT2", payment: "PAY_AMT2" },
  { month: "September 2005", status: "PAY_0", bill: "BILL_AMT1", payment: "PAY_AMT1" },
];

const STATUS_COLORS = [
  "#718b9a", "#91a7a8", "#7fae9b", "#aac49a", "#d0bf84", "#d8a96f",
  "#c98773", "#b87479", "#947b9c", "#7894bd", "#7d9b82", "#a78868",
];

function meanOfFields(row, fields) {
  const values = fields.map((field) => row[field]).filter(Number.isFinite);
  if (values.length !== fields.length) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function quantile(sortedValues, fraction) {
  if (!sortedValues.length) return null;
  const position = (sortedValues.length - 1) * fraction;
  const lowerIndex = Math.floor(position);
  const upperIndex = Math.ceil(position);
  const weight = position - lowerIndex;
  return sortedValues[lowerIndex] * (1 - weight) + sortedValues[upperIndex] * weight;
}

function summarizeMeasure(rows, read) {
  const values = rows.map(read).filter(Number.isFinite).sort((left, right) => left - right);
  if (!values.length) return { count: 0, missing: rows.length };
  return {
    count: values.length,
    missing: rows.length - values.length,
    minimum: values[0],
    percentile25: quantile(values, 0.25),
    median: quantile(values, 0.5),
    percentile75: quantile(values, 0.75),
    maximum: values[values.length - 1],
  };
}

function renderSelectionProfile(rows) {
  const groupDefinitions = [
    { label: "Selected for review", selected: true },
    { label: "Not selected", selected: false },
  ];
  const groups = groupDefinitions.map((definition) => {
    const members = rows.filter((row) => row.selected_for_review === definition.selected);
    const group = document.createElement("article");
    group.className = `selection-profile-group${definition.selected ? " is-selected" : ""}`;

    const heading = document.createElement("div");
    heading.className = "selection-profile-group-heading";
    const title = document.createElement("h4");
    title.textContent = definition.label;
    const size = document.createElement("span");
    const share = rows.length ? formatPercent(members.length / rows.length) : "—";
    size.textContent = `${formatCount(members.length)} customers · ${share} of portfolio`;
    heading.append(title, size);
    group.append(heading);

    if (!members.length) {
      const empty = document.createElement("p");
      empty.className = "selection-profile-empty";
      empty.textContent = "No customers fall into this group under the current capacity.";
      group.append(empty);
      return group;
    }

    const list = document.createElement("dl");
    list.className = "selection-profile-measures";
    PROFILE_MEASURES.forEach((measure) => {
      const summary = summarizeMeasure(members, measure.read);
      const item = document.createElement("div");
      item.className = "selection-profile-measure";
      const label = document.createElement("dt");
      label.textContent = measure.label;
      const values = document.createElement("dd");
      if (!summary.count) {
        values.textContent = "No available values";
      } else {
        const median = document.createElement("strong");
        median.textContent = `Median ${measure.format(summary.median)}`;
        const middle = document.createElement("span");
        middle.textContent = `Middle half: ${measure.format(summary.percentile25)}–${measure.format(summary.percentile75)}`;
        const range = document.createElement("span");
        range.textContent = `Range: ${measure.format(summary.minimum)}–${measure.format(summary.maximum)}`;
        const records = document.createElement("span");
        records.textContent = `${formatCount(summary.count)} available · ${formatCount(summary.missing)} missing`;
        values.append(median, middle, range, records);
      }
      item.append(label, values);
      list.append(item);
    });
    group.append(list);
    return group;
  });
  elements.selectionProfileGroups.replaceChildren(...groups);
}

function renderRepaymentStatusDistribution(rows) {
  const codeSet = new Set();
  MONTHLY_FEATURES.forEach(({ status }) => {
    rows.forEach((record) => {
      if (Number.isFinite(record[status])) codeSet.add(record[status]);
    });
  });
  const codes = [...codeSet].sort((left, right) => left - right);
  const colorByCode = new Map(codes.map((code, index) => [code, STATUS_COLORS[index % STATUS_COLORS.length]]));

  const months = MONTHLY_FEATURES.map(({ month, status }) => {
    const counts = new Map(codes.map((code) => [code, 0]));
    let available = 0;
    rows.forEach((record) => {
      const code = record[status];
      if (!Number.isFinite(code)) return;
      counts.set(code, (counts.get(code) ?? 0) + 1);
      available += 1;
    });

    const row = document.createElement("div");
    row.className = "repayment-month-row";
    row.setAttribute("role", "listitem");
    const heading = document.createElement("div");
    heading.className = "repayment-month-heading";
    const label = document.createElement("strong");
    label.textContent = month;
    const recordCount = document.createElement("span");
    recordCount.textContent = `${formatCount(available)} records`;
    heading.append(label, recordCount);

    const track = document.createElement("div");
    track.className = "repayment-status-track";
    const breakdown = [];
    codes.forEach((code) => {
      const count = counts.get(code) ?? 0;
      if (!count || !available) return;
      const share = count / available;
      const segment = document.createElement("span");
      const description = `Code ${code}: ${formatCount(count)} customers (${formatPercent(share)})`;
      segment.className = "repayment-status-segment";
      segment.style.flexBasis = `${share * 100}%`;
      segment.style.backgroundColor = colorByCode.get(code);
      segment.title = description;
      track.append(segment);
      breakdown.push({ code, count, share, description });
    });
    track.setAttribute("role", "img");
    track.setAttribute("aria-label", `${month} repayment status distribution: ${breakdown.map((item) => item.description).join("; ") || "no available records"}`);

    const legend = document.createElement("div");
    legend.className = "repayment-status-legend";
    breakdown.forEach(({ code, description }) => {
      const item = document.createElement("span");
      item.className = "repayment-status-key";
      const swatch = document.createElement("i");
      swatch.setAttribute("aria-hidden", "true");
      swatch.style.backgroundColor = colorByCode.get(code);
      const text = document.createElement("span");
      text.textContent = description;
      item.append(swatch, text);
      legend.append(item);
    });
    row.append(heading, track, legend);
    return row;
  });
  elements.repaymentStatusChart.replaceChildren(...months);
}

function renderMonthlyAmountSummary(rows, fieldName, target) {
  const tableRows = MONTHLY_FEATURES.map(({ month, [fieldName]: field }) => {
    const summary = summarizeMeasure(rows, (record) => record[field]);
    const row = document.createElement("tr");
    const values = [
      month,
      summary.count ? formatProfileNumber(summary.median) : "—",
      summary.count ? `${formatProfileNumber(summary.percentile25)}–${formatProfileNumber(summary.percentile75)}` : "—",
      summary.count ? `${formatProfileNumber(summary.minimum)}–${formatProfileNumber(summary.maximum)}` : "—",
      `${formatCount(summary.count)} available · ${formatCount(summary.missing)} missing`,
    ];
    values.forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    return row;
  });
  target.replaceChildren(...tableRows);
}

function formatImportanceScore(value) {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 6 }).format(value);
}

function renderModelImportance(reference) {
  if (!reference?.features?.length) {
    elements.modelImportanceChart.textContent = "Model reference results are unavailable.";
    return;
  }
  elements.importanceMethodDescription.textContent =
    `Permutation importance · ${reference.scoring_metric.replaceAll("_", " ")} · ${reference.evaluation_reference}.`;
  const maximumAbsoluteImportance = Math.max(
    ...reference.features.map((item) => Math.abs(item.importance_mean)),
    Number.EPSILON,
  );
  const rows = reference.features.map((item) => {
    const row = document.createElement("div");
    row.className = "model-importance-row";
    row.setAttribute("role", "listitem");
    const feature = document.createElement("div");
    feature.className = "model-importance-feature";
    const name = document.createElement("strong");
    name.textContent = item.feature;
    const description = document.createElement("span");
    description.textContent = item.description;
    feature.append(name, description);

    const track = document.createElement("div");
    track.className = "importance-score-track";
    track.setAttribute("role", "img");
    track.setAttribute("aria-label", `${item.feature}: mean Average Precision change ${formatImportanceScore(item.importance_mean)} after shuffling`);
    const bar = document.createElement("span");
    const width = Math.abs(item.importance_mean) / maximumAbsoluteImportance * 50;
    bar.className = `importance-score-bar${item.importance_mean < 0 ? " is-negative" : ""}`;
    bar.style.width = `${width}%`;
    if (item.importance_mean < 0) bar.style.right = "50%";
    track.append(bar);

    const score = document.createElement("div");
    score.className = "model-importance-score";
    const mean = document.createElement("strong");
    mean.textContent = formatImportanceScore(item.importance_mean);
    const spread = document.createElement("span");
    spread.textContent = `SD ${formatImportanceScore(item.importance_std)} across ${formatCount(reference.repeats)} shuffles`;
    score.append(mean, spread);
    row.append(feature, track, score);
    return row;
  });
  elements.modelImportanceChart.replaceChildren(...rows);
  elements.importanceReferenceNote.textContent =
    `Reference: ${reference.evaluation_reference}. Scores are mean Average Precision change across ${formatCount(reference.repeats)} shuffles (random seed ${reference.random_state}); the SD describes variation across those repeats, not a confidence interval. Bar lengths are relative to the largest absolute mean in this top-ten view. This fixed reference is not recalculated from the uploaded portfolio.`;
}

function renderFeatureInsights(rows, importanceReference) {
  elements.featureInsightsCount.textContent = `${formatCount(rows.length)} customers`;
  renderRepaymentStatusDistribution(rows);
  renderMonthlyAmountSummary(rows, "bill", elements.monthlyBillSummary);
  renderMonthlyAmountSummary(rows, "payment", elements.monthlyPaymentSummary);
  renderModelImportance(importanceReference);
}

function renderMetricCards(result) {
  const capacity = result.capacity;
  const summary = result.portfolio_summary.probability_summary;
  const metrics = [
    { label: "Customers scored", value: formatCount(result.population_count), help: "Full uploaded portfolio", icon: "▦" },
    { label: "Mean predicted risk", value: formatPercent(summary.mean), help: "Average model estimate", icon: "⌁" },
    { label: "Selected for review", value: formatCount(capacity.selected_count), help: "Under the supplied capacity", icon: "✓" },
    { label: "Unused capacity", value: formatCount(capacity.unused_capacity), help: "After tie-aware selection", icon: "↗" },
  ];

  elements.metrics.replaceChildren(...metrics.map((metric) => {
    const card = document.createElement("article");
    card.className = "metric-card";
    card.innerHTML = `
      <div class="metric-card-top">
        <span class="metric-label">${metric.label}</span>
        <span class="metric-icon" aria-hidden="true">${metric.icon}</span>
      </div>
      <strong class="metric-value">${metric.value}</strong>
      <span class="metric-help">${metric.help}</span>
    `;
    return card;
  }));
}

function renderRiskBands(summary) {
  const bands = summary.risk_bands;
  elements.riskBands.replaceChildren(...bands.map((band) => {
    const row = document.createElement("div");
    row.className = "band-row";
    row.dataset.band = band.label;
    row.setAttribute("role", "listitem");

    const label = document.createElement("span");
    label.className = "band-label";
    label.textContent = band.label;

    const track = document.createElement("span");
    track.className = "band-track";
    track.setAttribute("aria-hidden", "true");
    const fill = document.createElement("span");
    fill.className = "band-fill";
    fill.style.width = `${Math.max(0, Math.min(1, band.portfolio_share)) * 100}%`;
    track.append(fill);

    const value = document.createElement("span");
    value.className = "band-value";
    value.innerHTML = `<strong>${formatCount(band.customer_count)}</strong> <span>· ${formatPercent(band.portfolio_share)}</span>`;
    row.append(label, track, value);
    return row;
  }));
  elements.riskReference.textContent = `${summary.risk_band_reference}. The fixed validation-cohort method is descriptive; these bands are not action thresholds.`;
}

function renderCapacity(result) {
  const capacity = result.capacity;
  const denominator = capacity.target_review_count;
  const utilization = denominator > 0 ? capacity.selected_count / denominator : 0;
  const safeUtilization = Math.max(0, Math.min(1, utilization));
  const percentage = denominator > 0 ? Math.round(safeUtilization * 100) : null;
  const degrees = safeUtilization * 360;

  elements.capacityRing.style.background = `conic-gradient(#438675 0deg ${degrees}deg, #e8efeb ${degrees}deg 360deg)`;
  elements.capacityPercent.textContent = percentage === null ? "—" : `${percentage}%`;

  const items = [
    { label: "Requested", count: capacity.requested_review_count, note: "Analyst capacity" },
    { label: "Selected", count: capacity.selected_count, note: "Entered the queue" },
    { label: "Unused", count: capacity.unused_capacity, note: "Tie-aware remainder" },
  ];
  elements.capacityLegend.replaceChildren(...items.map((item) => {
    const entry = document.createElement("div");
    entry.className = "legend-item";
    const dot = document.createElement("span");
    dot.className = "legend-dot";
    dot.setAttribute("aria-hidden", "true");
    const copy = document.createElement("span");
    copy.className = "legend-copy";
    const strong = document.createElement("strong");
    strong.textContent = `${item.label}: ${formatCount(item.count)}`;
    const note = document.createElement("span");
    note.textContent = item.note;
    copy.append(strong, note);
    entry.append(dot, copy);
    return entry;
  }));

  if (denominator === 0) {
    elements.capacityFootnote.textContent = "No review capacity was requested; no customers were selected.";
  } else if (capacity.unused_capacity > 0) {
    elements.capacityFootnote.textContent = "Some capacity remained unused because the queue keeps equal-score customers together at the selection boundary.";
  } else {
    elements.capacityFootnote.textContent = "The requested target was filled. Equal-score groups are kept together at the selection boundary.";
  }
}

function getRiskBand(record) {
  const score = record.predicted_default_probability;
  return currentResult.portfolio_summary.risk_bands.find((band) =>
    (band.lower_bound_exclusive === null || score > band.lower_bound_exclusive)
    && (band.upper_bound_inclusive === null || score <= band.upper_bound_inclusive)
  )?.label ?? "Unassigned";
}

function resetExploreFilters() {
  elements.customerIdFilter.value = "";
  elements.scoreMinFilter.value = "0";
  elements.scoreMaxFilter.value = "1";
  elements.riskBandFilter.value = "";
  elements.reviewStatusFilter.value = "";
  elements.featureFilter.value = "";
  elements.featureValueControl.replaceChildren();
  elements.featureValueControl.hidden = true;
  elements.filterMessage.textContent = "";
  currentPage = 0;
}

function initializeExploreFields() {
  const fields = dashboardConfig.required_columns.filter((field) => field !== "ID" && !DASHBOARD_FIELDS.has(field));
  elements.featureFilter.replaceChildren(new Option("No input filter", ""));
  elements.groupByField.replaceChildren(...fields.map((field) => new Option(field, field)));
  elements.featureFilter.append(...fields.map((field) => new Option(field, field)));
  elements.groupByField.value = "PAY_0";
}

function renderFeatureValueControl() {
  const field = elements.featureFilter.value;
  elements.featureValueControl.replaceChildren();
  if (!field || !currentPortfolio.length) {
    elements.featureValueControl.hidden = true;
    return;
  }
  elements.featureValueControl.hidden = false;
  if (CATEGORICAL_FIELDS.has(field)) {
    const label = document.createElement("label");
    label.className = "filter-control";
    const title = document.createElement("span");
    title.textContent = `${field} value`;
    const select = document.createElement("select");
    select.id = "feature-filter-value";
    select.append(new Option("All values", ""));
    [...new Set(currentPortfolio.map((row) => row[field]))]
      .sort((left, right) => left - right)
      .forEach((value) => select.append(new Option(String(value), String(value))));
    select.addEventListener("change", () => runExploreFilters(true));
    label.append(title, select);
    elements.featureValueControl.append(label);
    return;
  }

  const values = currentPortfolio.map((row) => row[field]);
  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  const label = document.createElement("span");
  label.textContent = `${field} range`;
  const inputs = document.createElement("div");
  inputs.className = "feature-range-inputs";
  for (const [caption, id, value] of [["Min", "feature-filter-min", minimum], ["Max", "feature-filter-max", maximum]]) {
    const inputLabel = document.createElement("label");
    inputLabel.className = "visually-hidden";
    inputLabel.htmlFor = id;
    inputLabel.textContent = `${field} ${caption.toLowerCase()}`;
    const input = document.createElement("input");
    input.type = "number";
    input.id = id;
    input.step = "any";
    input.value = String(value);
    input.dataset.bound = caption.toLowerCase();
    input.addEventListener("input", () => runExploreFilters(true));
    inputs.append(inputLabel, input);
  }
  elements.featureValueControl.append(label, inputs);
}

function numericQuantile(values, proportion) {
  const sorted = [...values].sort((left, right) => left - right);
  const position = (sorted.length - 1) * proportion;
  const lower = Math.floor(position);
  const fraction = position - lower;
  return sorted[lower + 1] === undefined
    ? sorted[lower]
    : sorted[lower] + fraction * (sorted[lower + 1] - sorted[lower]);
}

function getQuartileBoundaries(field) {
  if (!quartileBoundaryCache.has(field)) {
    const values = currentPortfolio.map((row) => row[field]);
    quartileBoundaryCache.set(field, [
      numericQuantile(values, 0.25),
      numericQuantile(values, 0.5),
      numericQuantile(values, 0.75),
    ]);
  }
  return quartileBoundaryCache.get(field);
}

function getQuartileIndex(value, field) {
  const [first, second, third] = getQuartileBoundaries(field);
  if (value <= first) return 0;
  if (value <= second) return 1;
  if (value <= third) return 2;
  return 3;
}

function getGroupLabel(value, field, index = null) {
  if (CATEGORICAL_FIELDS.has(field)) return String(value);
  const [first, second, third] = getQuartileBoundaries(field);
  const formatBoundary = (boundary) => boundary.toLocaleString(undefined, { maximumSignificantDigits: 7 });
  if (index === 0) return `≤ ${formatBoundary(first)}`;
  if (index === 1) return `${formatBoundary(first)} – ${formatBoundary(second)}`;
  if (index === 2) return `${formatBoundary(second)} – ${formatBoundary(third)}`;
  return `> ${formatBoundary(third)}`;
}

function applyExploreFilters() {
  const idQuery = elements.customerIdFilter.value.trim();
  const minimumScore = elements.scoreMinFilter.value === "" ? 0 : Number(elements.scoreMinFilter.value);
  const maximumScore = elements.scoreMaxFilter.value === "" ? 1 : Number(elements.scoreMaxFilter.value);
  if (minimumScore > maximumScore) {
    elements.filterMessage.textContent = "Minimum predicted risk must not exceed maximum predicted risk.";
    return null;
  }
  elements.filterMessage.textContent = "";
  const band = elements.riskBandFilter.value;
  const reviewStatus = elements.reviewStatusFilter.value;
  const field = elements.featureFilter.value;
  const categoryValue = document.querySelector("#feature-filter-value")?.value ?? "";
  const featureMinimum = document.querySelector("#feature-filter-min")?.value;
  const featureMaximum = document.querySelector("#feature-filter-max")?.value;

  return currentPortfolio.filter((record) => {
    const score = record.predicted_default_probability;
    if (idQuery && !String(record.customer_id).includes(idQuery)) return false;
    if (score < minimumScore || score > maximumScore) return false;
    if (band && getRiskBand(record) !== band) return false;
    if (reviewStatus === "selected" && !record.selected_for_review) return false;
    if (reviewStatus === "not-selected" && record.selected_for_review) return false;
    if (field && CATEGORICAL_FIELDS.has(field) && categoryValue && String(record[field]) !== categoryValue) return false;
    if (field && !CATEGORICAL_FIELDS.has(field)) {
      if (featureMinimum !== undefined && featureMinimum !== "" && record[field] < Number(featureMinimum)) return false;
      if (featureMaximum !== undefined && featureMaximum !== "" && record[field] > Number(featureMaximum)) return false;
    }
    return true;
  });
}

function renderScoreDistribution(rows) {
  const bins = Array.from({ length: 10 }, (_, index) => ({
    lower: index / 10,
    upper: (index + 1) / 10,
    count: 0,
  }));
  rows.forEach((record) => {
    const index = Math.min(9, Math.floor(record.predicted_default_probability * 10));
    bins[index].count += 1;
  });
  const denominator = rows.length;
  elements.scoreDistribution.replaceChildren(...bins.map((bin) => {
    const row = document.createElement("div");
    row.className = "distribution-row";
    row.setAttribute("role", "listitem");
    const label = document.createElement("span");
    label.className = "distribution-label";
    label.textContent = `${Math.round(bin.lower * 100)}–${Math.round(bin.upper * 100)}%`;
    const track = document.createElement("span");
    track.className = "distribution-track";
    track.setAttribute("aria-hidden", "true");
    const fill = document.createElement("span");
    fill.className = "distribution-fill";
    const share = denominator ? bin.count / denominator : 0;
    fill.style.width = `${share * 100}%`;
    track.append(fill);
    const value = document.createElement("span");
    value.className = "distribution-value";
    value.textContent = `${formatCount(bin.count)} · ${formatPercent(share)}`;
    row.append(label, track, value);
    return row;
  }));
}

function renderGroupSummary(rows) {
  const field = elements.groupByField.value;
  if (!rows.length) {
    const emptyRow = document.createElement("tr");
    const message = document.createElement("td");
    message.colSpan = 5;
    message.textContent = "No customers match the current filters.";
    emptyRow.append(message);
    elements.groupSummaryBody.replaceChildren(emptyRow);
    elements.groupTableNote.textContent = "Adjust or reset the filters to compare groups.";
    return;
  }
  const groups = new Map();
  rows.forEach((record) => {
    const groupKey = CATEGORICAL_FIELDS.has(field)
      ? String(record[field])
      : String(getQuartileIndex(record[field], field));
    if (!groups.has(groupKey)) {
      const groupIndex = CATEGORICAL_FIELDS.has(field) ? null : Number(groupKey);
      groups.set(groupKey, { label: getGroupLabel(record[field], field, groupIndex), records: [] });
    }
    groups.get(groupKey).records.push(record);
  });
  const orderedGroups = [...groups.entries()].sort((left, right) => {
    if (CATEGORICAL_FIELDS.has(field)) return Number(left[0]) - Number(right[0]);
    return Number(left[0]) - Number(right[0]);
  });
  elements.groupSummaryBody.replaceChildren(...orderedGroups.map(([, group]) => {
    const { label, records } = group;
    const row = document.createElement("tr");
    const values = [
      label,
      formatCount(records.length),
      formatPercent(rows.length ? records.length / rows.length : 0),
      formatPercent(records.reduce((sum, item) => sum + item.predicted_default_probability, 0) / records.length),
      formatCount(records.filter((item) => item.selected_for_review).length),
    ];
    values.forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    return row;
  }));
  elements.groupTableNote.textContent = CATEGORICAL_FIELDS.has(field)
    ? `Encoded values for ${field} are shown as supplied; group shares use the filtered cohort.`
    : `Quartile boundaries for ${field} are calculated from the full portfolio; shares use the filtered cohort.`;
}

function renderCustomerTable(rows) {
  const pageCount = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  currentPage = Math.min(currentPage, pageCount - 1);
  const start = currentPage * PAGE_SIZE;
  const visibleRows = rows.slice(start, start + PAGE_SIZE);
  const tableRows = visibleRows.map((record) => {
    const row = document.createElement("tr");
    const values = [
      formatCount(record.risk_rank),
      formatCount(record.customer_id),
      formatPercent(record.predicted_default_probability),
      getRiskBand(record),
      record.selected_for_review ? "Selected" : "Not selected",
    ];
    values.forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    const detailCell = document.createElement("td");
    const detailButton = document.createElement("button");
    detailButton.className = "secondary-button detail-button";
    detailButton.type = "button";
    detailButton.textContent = "Inspect";
    detailButton.setAttribute("aria-label", `Inspect customer ${record.customer_id}`);
    detailButton.addEventListener("click", () => showCustomerDetail(record));
    detailCell.append(detailButton);
    row.append(detailCell);
    return row;
  });
  if (!rows.length) {
    const emptyRow = document.createElement("tr");
    const message = document.createElement("td");
    message.colSpan = 6;
    message.textContent = "No customers match the current filters.";
    emptyRow.append(message);
    tableRows.push(emptyRow);
  }
  elements.customerResultsBody.replaceChildren(...tableRows);
  const first = rows.length ? start + 1 : 0;
  const last = Math.min(start + PAGE_SIZE, rows.length);
  elements.pageCount.textContent = `${formatCount(first)}–${formatCount(last)} of ${formatCount(rows.length)}`;
  elements.pageStatus.textContent = `Page ${currentPage + 1} of ${pageCount}`;
  elements.previousPage.disabled = currentPage === 0;
  elements.nextPage.disabled = currentPage >= pageCount - 1;
}

function runExploreFilters(resetPage = false) {
  if (resetPage) currentPage = 0;
  const rows = applyExploreFilters();
  if (rows === null) return;
  filteredPortfolio = rows;
  elements.exploreCount.textContent = `${formatCount(rows.length)} of ${formatCount(currentPortfolio.length)} customers`;
  renderScoreDistribution(rows);
  renderGroupSummary(rows);
  renderCustomerTable(rows);
}

function renderQueueView(result) {
  const capacity = result.capacity;
  queuePage = 0;
  elements.queuePopulationCount.textContent = `${formatCount(result.population_count)} customers scored`;
  const utilization = capacity.target_review_count > 0
    ? formatPercent(capacity.selected_count / capacity.target_review_count)
    : "—";
  const metrics = [
    { label: "Requested capacity", value: formatCount(capacity.requested_review_count), help: "Analyst-entered limit" },
    { label: "Target count", value: formatCount(capacity.target_review_count), help: "Capped at portfolio size" },
    { label: "Selected for review", value: formatCount(capacity.selected_count), help: `${utilization} of target filled` },
    { label: "Unused capacity", value: formatCount(capacity.unused_capacity), help: "Target minus selected" },
  ];
  elements.queueMetricGrid.replaceChildren(...metrics.map((metric) => {
    const card = document.createElement("article");
    card.className = "metric-card queue-metric-card";
    const label = document.createElement("span");
    label.className = "metric-label";
    label.textContent = metric.label;
    const value = document.createElement("strong");
    value.className = "metric-value";
    value.textContent = metric.value;
    const help = document.createElement("span");
    help.className = "metric-help";
    help.textContent = metric.help;
    card.append(label, value, help);
    return card;
  }));

  const reasonGroups = new Map();
  result.customers.forEach((record) => {
    if (!reasonGroups.has(record.reason_code)) {
      reasonGroups.set(record.reason_code, { reason: record.reason, count: 0 });
    }
    reasonGroups.get(record.reason_code).count += 1;
  });
  elements.queueReasonsBody.replaceChildren(...[...reasonGroups.values()].map((group) => {
    const row = document.createElement("tr");
    const reason = document.createElement("td");
    reason.textContent = group.reason;
    const count = document.createElement("td");
    count.textContent = formatCount(group.count);
    row.append(reason, count);
    return row;
  }));
  renderSelectedQueue(result.customers.filter((record) => record.selected_for_review));
}

function renderSelectedQueue(selectedCustomers) {
  const pageCount = Math.max(1, Math.ceil(selectedCustomers.length / PAGE_SIZE));
  queuePage = Math.min(queuePage, pageCount - 1);
  const start = queuePage * PAGE_SIZE;
  const currentRows = selectedCustomers.slice(start, start + PAGE_SIZE);
  const rows = currentRows.map((record) => {
    const row = document.createElement("tr");
    [
      formatCount(record.risk_rank),
      formatCount(record.customer_id),
      formatPercent(record.predicted_default_probability),
      record.reason,
    ].forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
    row.append(cell);
    });
    const detailCell = document.createElement("td");
    const detailButton = document.createElement("button");
    detailButton.className = "secondary-button detail-button";
    detailButton.type = "button";
    detailButton.textContent = "Inspect";
    detailButton.setAttribute("aria-label", `Inspect customer ${record.customer_id}`);
    detailButton.addEventListener("click", () => showCustomerDetail(record));
    detailCell.append(detailButton);
    row.append(detailCell);
    return row;
  });
  if (!selectedCustomers.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 5;
    cell.textContent = "No customers were selected under this capacity.";
    row.append(cell);
    rows.push(row);
  }
  elements.selectedQueueBody.replaceChildren(...rows);
  const first = selectedCustomers.length ? start + 1 : 0;
  const last = Math.min(start + PAGE_SIZE, selectedCustomers.length);
  elements.queuePageCount.textContent = `${formatCount(first)}–${formatCount(last)} of ${formatCount(selectedCustomers.length)}`;
  elements.queuePageStatus.textContent = `Page ${queuePage + 1} of ${pageCount}`;
  elements.queuePreviousPage.disabled = queuePage === 0;
  elements.queueNextPage.disabled = queuePage >= pageCount - 1;
}

function setActiveView(view) {
  if (view !== "overview" && !currentResult) return;
  activeView = view;
  elements.results.hidden = view !== "overview" || !currentResult;
  elements.exploreView.hidden = view !== "explore" || !currentResult;
  elements.queueView.hidden = view !== "queue" || !currentResult;
  elements.featureInsightsView.hidden = view !== "feature-insights" || !currentResult;
  elements.emptyState.hidden = Boolean(currentResult);
  elements.viewLinks.forEach((link) => {
    const active = link.dataset.view === view;
    link.classList.toggle("is-active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  const viewLabels = {
    overview: "Overview",
    explore: "Explore portfolio",
    queue: "Review queue",
    "feature-insights": "Feature insights",
  };
  document.querySelector(".breadcrumb").lastChild.textContent = ` ${viewLabels[view]}`;
}

function renderOverview(result, inputRows) {
  currentResult = result;
  currentInputRows = inputRows;
  const inputsById = new Map(inputRows.map((row) => [row.ID, row]));
  currentPortfolio = result.customers.map((scoredRow) => ({
    ...inputsById.get(scoredRow.customer_id),
    ...scoredRow,
  }));
  quartileBoundaryCache.clear();
  initializeExploreFields();
  resetExploreFilters();
  renderQueueView(result);
  renderSelectionProfile(currentPortfolio);
  renderFeatureInsights(currentPortfolio, dashboardConfig?.model_feature_importance);
  [elements.exportFiltered, elements.exportRanking, elements.exportQueue].forEach((button) => { button.disabled = false; });
  renderMetricCards(result);
  renderRiskBands(result.portfolio_summary);
  renderCapacity(result);
  elements.portfolioCount.textContent = `${formatCount(result.population_count)} customers`;
  elements.analysisMetaText.textContent = `Scored ${new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
  elements.analysisMeta.hidden = false;
  runExploreFilters();
  setActiveView("overview");
  elements.results.scrollIntoView({ behavior: "smooth", block: "start" });
}

function buildAnalystFilters() {
  const filters = {
    minimum_probability: Number(elements.scoreMinFilter.value || 0),
    maximum_probability: Number(elements.scoreMaxFilter.value || 1),
  };
  if (elements.riskBandFilter.value) filters.risk_band = elements.riskBandFilter.value;
  if (elements.reviewStatusFilter.value) filters.review_status = elements.reviewStatusFilter.value;

  const feature = elements.featureFilter.value;
  if (feature) {
    filters.feature = feature;
    const categoryValue = document.querySelector("#feature-filter-value")?.value;
    if (categoryValue !== undefined && categoryValue !== "") {
      filters.category_value = Number(categoryValue);
    } else {
      const minimum = document.querySelector("#feature-filter-min")?.value;
      const maximum = document.querySelector("#feature-filter-max")?.value;
      if (minimum !== undefined && minimum !== "") filters.feature_minimum = Number(minimum);
      if (maximum !== undefined && maximum !== "") filters.feature_maximum = Number(maximum);
    }
  }
  return filters;
}

function clearAnalystAnswer() {
  elements.analystState.textContent = "";
  elements.analystClaims.replaceChildren();
  elements.analystCitations.replaceChildren();
  elements.analystDisclaimer.textContent = "";
}

function renderAnalystAnswer(answer) {
  clearAnalystAnswer();
  if (answer.status === "refused") {
    elements.analystState.textContent = answer.refusal_code === "small_cell_suppressed"
      ? "This response is unavailable because the filtered group is below the privacy threshold. Broaden the cohort and try again."
      : "This question could not be answered from the approved portfolio evidence. Try asking about a displayed metric, cohort summary, queue behavior, or explanation limitation.";
  } else {
    elements.analystState.textContent = "Generated commentary";
    answer.claims.forEach((claim) => {
      const paragraph = document.createElement("p");
      paragraph.className = `analyst-claim analyst-claim-${claim.kind}`;
      paragraph.textContent = claim.text;
      elements.analystClaims.append(paragraph);
    });
    const citations = document.createElement("ul");
    citations.className = "analyst-citation-list";
    answer.citations.forEach((citation) => {
      const item = document.createElement("li");
      const label = document.createElement("strong");
      label.textContent = citation.key.split(".").map((part) => part
        .replaceAll("_", " ")
        .replace(/\b\w/g, (letter) => letter.toUpperCase())).join(" · ");
      const value = document.createElement("span");
      const formatted = typeof citation.value === "number" && citation.unit === "probability"
        ? formatPercent(citation.value)
        : typeof citation.value === "object"
          ? JSON.stringify(citation.value)
          : String(citation.value);
      value.textContent = `${formatted}${citation.unit ? ` ${citation.unit}` : ""} · ${citation.scope.replaceAll("_", " ")}`;
      const definition = document.createElement("small");
      definition.textContent = citation.definition;
      item.append(label, value, definition);
      citations.append(item);
    });
    if (citations.childElementCount) elements.analystCitations.append(citations);
  }
  elements.analystDisclaimer.textContent = answer.disclaimer || "Generated commentary is not an outcome, cause, or recommendation.";
  elements.analystAnswer.hidden = false;
}

async function askAnalyst(question) {
  if (!currentResult || !currentInputRows.length) return;
  elements.analystAnswer.hidden = false;
  elements.analystAnswer.setAttribute("aria-busy", "true");
  elements.analystState.textContent = "Preparing an evidence-based answer…";
  elements.analystClaims.replaceChildren();
  elements.analystCitations.replaceChildren();
  elements.analystDisclaimer.textContent = "";
  elements.analystSubmit.disabled = true;
  document.querySelectorAll("[data-analyst-prompt]").forEach((button) => { button.disabled = true; });
  try {
    const response = await fetch("/v1/analyst-answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        customers: currentInputRows,
        max_review_count: currentResult.capacity.requested_review_count,
        filters: buildAnalystFilters(),
        group_by: elements.groupByField.value || null,
        question,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      const message = payload?.error?.message;
      const details = payload?.error?.details?.filter(Boolean).join(" ");
      if (response.status === 503) {
        throw new Error("Generated insights are not enabled yet. Portfolio scoring and dashboard summaries are still available.");
      }
      throw new Error(details || message || "The insight request could not be completed.");
    }
    renderAnalystAnswer(payload);
  } catch (error) {
    clearAnalystAnswer();
    elements.analystState.textContent = error instanceof TypeError
      ? "The insight service is temporarily unavailable. Your portfolio analysis is still available."
      : error.message || "The insight request could not be completed.";
    elements.analystDisclaimer.textContent = "No answer was generated. Your deterministic dashboard results remain unchanged.";
    elements.analystAnswer.hidden = false;
  } finally {
    elements.analystAnswer.setAttribute("aria-busy", "false");
    elements.analystSubmit.disabled = false;
    document.querySelectorAll("[data-analyst-prompt]").forEach((button) => { button.disabled = false; });
  }
}

async function readSelectedFile() {
  if (!selectedFile) throw new Error("Choose a CSV file before running the analysis.");
  const text = await selectedFile.text();
  return validateCsvRows(parseCsv(text));
}

async function loadDashboardConfig() {
  const response = await fetch("/v1/dashboard-config");
  if (!response.ok) throw new Error("The dashboard couldn’t load its setup details. Refresh and try again.");
  dashboardConfig = await response.json();
  elements.fileHint.textContent = `ID and all 23 predictors · up to ${formatCount(dashboardConfig.max_customer_rows)} customers`;
  elements.capacity.max = String(dashboardConfig.max_customer_rows);
}

async function checkService() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("Portfolio scoring is temporarily unavailable.");
    const health = await response.json();
    if (!health.model_loaded) throw new Error("Portfolio scoring isn’t ready yet. Try again shortly.");
    setServiceStatus(true, "Ready to score portfolios");
  } catch (error) {
    setServiceStatus(false, "Portfolio scoring is temporarily unavailable.");
  }
}

elements.file.addEventListener("change", () => {
  selectedFile = elements.file.files?.[0] ?? null;
  clearMessage();
  if (selectedFile) {
    elements.fileName.textContent = selectedFile.name;
    elements.fileHint.textContent = `${(selectedFile.size / 1024).toFixed(0)} KB · ready to validate`;
    elements.fileName.title = selectedFile.name;
  } else {
    elements.fileName.textContent = "Choose a CSV file";
  }
});

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessage();
  elements.runButton.disabled = true;
  elements.runButton.querySelector("span:first-child").textContent = "Scoring portfolio…";

  try {
    if (!dashboardConfig) await loadDashboardConfig();
    const customers = await readSelectedFile();
    if (elements.capacity.value.trim() === "") {
      throw new Error("Enter a review capacity.");
    }
    const capacity = Number(elements.capacity.value);
    if (!Number.isSafeInteger(capacity) || capacity < 0) {
      throw new Error("Review capacity must be a non-negative whole number.");
    }

    const response = await fetch("/v1/review-queue", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ customers, max_review_count: capacity }),
    });
    const payload = await response.json();
    if (!response.ok) {
      const details = payload?.error?.details?.filter(Boolean).join(" ");
      throw new Error(details || payload?.error?.message || "The scoring request failed.");
    }

    renderOverview(payload, customers);
    setServiceStatus(true, "Ready to score portfolios");
    showMessage(`Analysis complete for ${formatCount(payload.population_count)} customers.`, "success");
  } catch (error) {
    const message = error instanceof TypeError
      ? "Portfolio scoring is temporarily unavailable. Check your connection and try again."
      : error.message || "The portfolio could not be scored.";
    showMessage(message);
  } finally {
    elements.runButton.disabled = false;
    elements.runButton.querySelector("span:first-child").textContent = "Run analysis";
  }
});

elements.analystForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = elements.analystQuestion.value.trim();
  if (!question) {
    elements.analystQuestion.focus();
    return;
  }
  await askAnalyst(question);
});

document.querySelectorAll("[data-analyst-prompt]").forEach((button) => {
  button.addEventListener("click", async () => {
    const question = button.dataset.analystPrompt;
    elements.analystQuestion.value = question;
    await askAnalyst(question);
  });
});

elements.healthCheck.addEventListener("click", checkService);
elements.closeCustomerDialog.addEventListener("click", () => elements.customerDialog.close());
elements.exportFiltered.addEventListener("click", () => exportRows(filteredPortfolio, "filtered-portfolio.csv", "Current Explore filters"));
elements.exportRanking.addEventListener("click", () => exportRows(currentPortfolio, "portfolio-ranking.csv", "Full scored portfolio"));
elements.exportQueue.addEventListener("click", () => exportRows(currentPortfolio.filter((row) => row.selected_for_review), "selected-review-queue.csv", "Selected review queue"));

elements.viewLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    setActiveView(link.dataset.view);
    if (currentResult) window.location.hash = link.dataset.view;
  });
});

[
  elements.customerIdFilter,
  elements.scoreMinFilter,
  elements.scoreMaxFilter,
  elements.riskBandFilter,
  elements.reviewStatusFilter,
].forEach((control) => control.addEventListener("input", () => runExploreFilters(true)));
[
  elements.riskBandFilter,
  elements.reviewStatusFilter,
].forEach((control) => control.addEventListener("change", () => runExploreFilters(true)));
elements.featureFilter.addEventListener("change", () => {
  renderFeatureValueControl();
  runExploreFilters(true);
});
elements.groupByField.addEventListener("change", () => runExploreFilters(true));
elements.resetFilters.addEventListener("click", () => {
  resetExploreFilters();
  runExploreFilters(true);
});
elements.previousPage.addEventListener("click", () => {
  currentPage = Math.max(0, currentPage - 1);
  renderCustomerTable(filteredPortfolio);
});
elements.nextPage.addEventListener("click", () => {
  currentPage += 1;
  renderCustomerTable(filteredPortfolio);
});
elements.queuePreviousPage.addEventListener("click", () => {
  queuePage = Math.max(0, queuePage - 1);
  renderSelectedQueue(currentResult.customers.filter((record) => record.selected_for_review));
});
elements.queueNextPage.addEventListener("click", () => {
  queuePage += 1;
  renderSelectedQueue(currentResult.customers.filter((record) => record.selected_for_review));
});

loadDashboardConfig()
  .then(checkService)
  .catch(() => setServiceStatus(false, "Portfolio scoring is temporarily unavailable."));
