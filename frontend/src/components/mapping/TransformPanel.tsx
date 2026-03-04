import { useState } from "react";
import {
  Box,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  Paper,
  Collapse,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import type { TransformConfig } from "../../types";

const TRANSFORM_TYPES = [
  { value: "rename", label: "Rename Columns" },
  { value: "filter", label: "Filter Rows" },
  { value: "sort", label: "Sort" },
  { value: "format_date", label: "Format Date" },
  { value: "format_number", label: "Format Number" },
  { value: "computed", label: "Computed Column" },
];

interface Props {
  transforms: TransformConfig[];
  onChange: (transforms: TransformConfig[]) => void;
}

export default function TransformPanel({ transforms, onChange }: Props) {
  const [expanded, setExpanded] = useState(false);

  const addTransform = (type: string) => {
    onChange([...transforms, { type, params: {} }]);
  };

  const removeTransform = (index: number) => {
    onChange(transforms.filter((_, i) => i !== index));
  };

  const updateParams = (index: number, params: Record<string, unknown>) => {
    const updated = [...transforms];
    updated[index] = { ...updated[index], params };
    onChange(updated);
  };

  return (
    <Box>
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          cursor: "pointer",
          gap: 0.5,
        }}
        onClick={() => setExpanded(!expanded)}
      >
        {expanded ? (
          <ExpandLessIcon fontSize="small" />
        ) : (
          <ExpandMoreIcon fontSize="small" />
        )}
        <Typography variant="caption" color="text.secondary">
          Transforms ({transforms.length})
        </Typography>
      </Box>

      <Collapse in={expanded}>
        <Box sx={{ mt: 1, display: "flex", flexDirection: "column", gap: 1 }}>
          {transforms.map((t, i) => (
            <Paper key={i} variant="outlined" sx={{ p: 1 }}>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  mb: 0.5,
                }}
              >
                <Typography variant="caption" fontWeight="bold">
                  {TRANSFORM_TYPES.find((tt) => tt.value === t.type)?.label ??
                    t.type}
                </Typography>
                <IconButton size="small" onClick={() => removeTransform(i)}>
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Box>
              <TransformParamsEditor
                type={t.type}
                params={t.params}
                onChange={(params) => updateParams(i, params)}
              />
            </Paper>
          ))}

          <FormControl size="small" sx={{ maxWidth: 200 }}>
            <InputLabel>Add Transform</InputLabel>
            <Select
              value=""
              label="Add Transform"
              onChange={(e) => {
                if (e.target.value) addTransform(e.target.value);
              }}
            >
              {TRANSFORM_TYPES.map((tt) => (
                <MenuItem key={tt.value} value={tt.value}>
                  <AddIcon fontSize="small" sx={{ mr: 0.5 }} />
                  {tt.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      </Collapse>
    </Box>
  );
}

function TransformParamsEditor({
  type,
  params,
  onChange,
}: {
  type: string;
  params: Record<string, unknown>;
  onChange: (params: Record<string, unknown>) => void;
}) {
  const setParam = (key: string, value: unknown) => {
    onChange({ ...params, key: undefined, [key]: value });
  };

  switch (type) {
    case "rename":
      return (
        <TextField
          size="small"
          fullWidth
          label='Columns (JSON: {"old": "new"})'
          value={
            typeof params.columns === "string"
              ? params.columns
              : JSON.stringify(params.columns ?? {})
          }
          onChange={(e) => {
            try {
              onChange({ columns: JSON.parse(e.target.value) });
            } catch {
              onChange({ columns: e.target.value });
            }
          }}
        />
      );
    case "filter":
      return (
        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
          <TextField
            size="small"
            label="Column"
            value={(params.column as string) ?? ""}
            onChange={(e) => setParam("column", e.target.value)}
          />
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Operator</InputLabel>
            <Select
              value={(params.operator as string) ?? "equals"}
              label="Operator"
              onChange={(e) => setParam("operator", e.target.value)}
            >
              <MenuItem value="equals">Equals</MenuItem>
              <MenuItem value="not_equals">Not Equals</MenuItem>
              <MenuItem value="contains">Contains</MenuItem>
              <MenuItem value="gt">Greater Than</MenuItem>
              <MenuItem value="lt">Less Than</MenuItem>
            </Select>
          </FormControl>
          <TextField
            size="small"
            label="Value"
            value={(params.value as string) ?? ""}
            onChange={(e) => setParam("value", e.target.value)}
          />
        </Box>
      );
    case "sort":
      return (
        <Box sx={{ display: "flex", gap: 1 }}>
          <TextField
            size="small"
            label="Columns (comma-separated)"
            value={
              Array.isArray(params.columns)
                ? (params.columns as string[]).join(", ")
                : ""
            }
            onChange={(e) =>
              setParam(
                "columns",
                e.target.value.split(",").map((s) => s.trim())
              )
            }
          />
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Order</InputLabel>
            <Select
              value={params.ascending === false ? "desc" : "asc"}
              label="Order"
              onChange={(e) =>
                setParam("ascending", e.target.value === "asc")
              }
            >
              <MenuItem value="asc">Ascending</MenuItem>
              <MenuItem value="desc">Descending</MenuItem>
            </Select>
          </FormControl>
        </Box>
      );
    case "format_date":
      return (
        <Box sx={{ display: "flex", gap: 1 }}>
          <TextField
            size="small"
            label="Column"
            value={(params.column as string) ?? ""}
            onChange={(e) => setParam("column", e.target.value)}
          />
          <TextField
            size="small"
            label="Format (e.g. %m/%d/%Y)"
            value={(params.format as string) ?? ""}
            onChange={(e) => setParam("format", e.target.value)}
          />
        </Box>
      );
    case "format_number":
      return (
        <Box sx={{ display: "flex", gap: 1 }}>
          <TextField
            size="small"
            label="Column"
            value={(params.column as string) ?? ""}
            onChange={(e) => setParam("column", e.target.value)}
          />
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Style</InputLabel>
            <Select
              value={(params.style as string) ?? "decimal"}
              label="Style"
              onChange={(e) => setParam("style", e.target.value)}
            >
              <MenuItem value="decimal">Decimal</MenuItem>
              <MenuItem value="currency">Currency</MenuItem>
              <MenuItem value="percentage">Percentage</MenuItem>
            </Select>
          </FormControl>
          <TextField
            size="small"
            label="Decimals"
            type="number"
            value={(params.decimals as number) ?? 2}
            onChange={(e) => setParam("decimals", Number(e.target.value))}
            sx={{ width: 80 }}
          />
        </Box>
      );
    case "computed":
      return (
        <Box sx={{ display: "flex", gap: 1 }}>
          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel>Operation</InputLabel>
            <Select
              value={(params.operation as string) ?? "row_total"}
              label="Operation"
              onChange={(e) => setParam("operation", e.target.value)}
            >
              <MenuItem value="row_total">Row Total</MenuItem>
              <MenuItem value="agg_sum">Sum</MenuItem>
              <MenuItem value="agg_mean">Mean</MenuItem>
              <MenuItem value="agg_count">Count</MenuItem>
            </Select>
          </FormControl>
          <TextField
            size="small"
            label="Output Column"
            value={(params.output_column as string) ?? ""}
            onChange={(e) => setParam("output_column", e.target.value)}
          />
        </Box>
      );
    default:
      return (
        <TextField
          size="small"
          fullWidth
          label="Params (JSON)"
          value={JSON.stringify(params)}
          onChange={(e) => {
            try {
              onChange(JSON.parse(e.target.value));
            } catch {
              /* ignore parse errors during typing */
            }
          }}
        />
      );
  }
}
