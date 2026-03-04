import { useState } from "react";
import {
  Box,
  Button,
  CircularProgress,
  Typography,
} from "@mui/material";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";
import type {
  TemplateMarker,
  DataSource,
  MappingEntry,
  AutoResolutionMatch,
} from "../types";
import { autoResolve } from "../api/client";
import MappingCard from "./mapping/MappingCard";

interface Props {
  projectId: number;
  markers: TemplateMarker[];
  dataSources: DataSource[];
  mappings: MappingEntry[];
  onMappingsChange: (mappings: MappingEntry[]) => void;
}

export default function MappingPanel({
  projectId,
  markers,
  dataSources,
  mappings,
  onMappingsChange,
}: Props) {
  const [autoMatches, setAutoMatches] = useState<
    Record<string, AutoResolutionMatch>
  >({});
  const [resolving, setResolving] = useState(false);

  const getMapping = (markerId: string) =>
    mappings.find((m) => m.markerId === markerId);

  const updateMapping = (markerId: string, updates: Partial<MappingEntry>) => {
    const existing = mappings.findIndex((m) => m.markerId === markerId);
    const newMappings = [...mappings];
    if (existing >= 0) {
      newMappings[existing] = { ...newMappings[existing], ...updates };
    } else {
      newMappings.push({
        markerId,
        dataSource: "",
        ...updates,
      });
    }
    onMappingsChange(newMappings);
  };

  const removeMapping = (markerId: string) => {
    onMappingsChange(mappings.filter((m) => m.markerId !== markerId));
  };

  const handleAutoResolve = async () => {
    setResolving(true);
    try {
      const report = await autoResolve(projectId);

      // Build match lookup
      const matchMap: Record<string, AutoResolutionMatch> = {};
      for (const match of report.matches) {
        matchMap[match.markerId] = match;
      }
      setAutoMatches(matchMap);

      // Apply auto-resolved matches as mappings (only for unmapped markers)
      const newMappings = [...mappings];
      for (const match of report.matches) {
        const existing = newMappings.findIndex(
          (m) => m.markerId === match.markerId
        );
        if (existing < 0) {
          newMappings.push({
            markerId: match.markerId,
            dataSource: match.dataSource,
            field: match.field ?? undefined,
            sheet: match.sheet ?? undefined,
            path: match.path ?? undefined,
          });
        }
      }
      onMappingsChange(newMappings);
    } catch (err) {
      console.error("Auto-resolve failed:", err);
    } finally {
      setResolving(false);
    }
  };

  if (markers.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        No mappable markers found. Upload a template first.
      </Typography>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
        <Typography variant="subtitle1">Marker Mappings</Typography>
        {dataSources.length > 0 && (
          <Button
            size="small"
            startIcon={
              resolving ? (
                <CircularProgress size={16} />
              ) : (
                <AutoFixHighIcon />
              )
            }
            onClick={handleAutoResolve}
            disabled={resolving}
          >
            Auto-Resolve
          </Button>
        )}
      </Box>

      {markers.map((marker) => (
        <MappingCard
          key={marker.id}
          marker={marker}
          mapping={getMapping(marker.id)}
          dataSources={dataSources}
          autoMatch={autoMatches[marker.id]}
          onUpdate={(updates) => updateMapping(marker.id, updates)}
          onRemove={() => removeMapping(marker.id)}
        />
      ))}
    </Box>
  );
}
