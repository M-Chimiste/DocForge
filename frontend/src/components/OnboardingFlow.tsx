import { useState } from "react";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Step,
  StepLabel,
  Stepper,
  Typography,
} from "@mui/material";

interface OnboardingFlowProps {
  open: boolean;
  onClose: () => void;
}

const steps = [
  {
    label: "Upload a Template",
    description:
      "DocForge uses .docx templates with red-formatted text (#FF0000) as instructions. " +
      "Any text colored in exact red is treated as a marker — a placeholder for content that " +
      "will be filled in automatically during document generation.",
  },
  {
    label: "Add Data Sources",
    description:
      "Upload data files that contain the content you want to fill into your template markers. " +
      "Supported formats include Excel (.xlsx, .xls), CSV, JSON, YAML, plain text, " +
      "Word (.docx), PowerPoint (.pptx), and PDF.",
  },
  {
    label: "Map Markers to Data",
    description:
      "Each red-text marker in your template needs to be mapped to a data source field. " +
      "Use the Auto-Resolve feature to automatically match markers to the most likely data fields, " +
      "or map them manually for full control.",
  },
  {
    label: "Generate Your Document",
    description:
      "Once your markers are mapped, click Generate to produce your final document. " +
      "If you have LLM-type markers and an LLM provider configured, AI-generated content will " +
      "be included automatically. LLM support is optional — all other features work without it.",
  },
];

export default function OnboardingFlow({ open, onClose }: OnboardingFlowProps) {
  const [activeStep, setActiveStep] = useState(0);

  const handleNext = () => {
    if (activeStep === steps.length - 1) {
      setActiveStep(0);
      onClose();
    } else {
      setActiveStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleClose = () => {
    setActiveStep(0);
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      aria-labelledby="onboarding-dialog-title"
    >
      <DialogTitle id="onboarding-dialog-title">
        Welcome to DocForge
      </DialogTitle>
      <DialogContent>
        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
          {steps.map((step) => (
            <Step key={step.label}>
              <StepLabel>{step.label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        <Box sx={{ minHeight: 120, px: 1 }}>
          <Typography variant="h6" gutterBottom>
            {steps[activeStep].label}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {steps[activeStep].description}
          </Typography>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} color="inherit">
          Skip
        </Button>
        <Box sx={{ flex: 1 }} />
        <Button onClick={handleBack} disabled={activeStep === 0}>
          Back
        </Button>
        <Button variant="contained" onClick={handleNext}>
          {activeStep === steps.length - 1 ? "Finish" : "Next"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
