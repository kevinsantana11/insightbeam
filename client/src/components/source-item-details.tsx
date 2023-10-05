import React, { FC } from "react";
import { ArticleAnalysis, SourceItem } from "../schemas";
import { BaseAnalysisSection } from "./base-analysis-section";
import { CounterAnalysisSection } from "./counter-analysis-section";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  AccordionSummaryProps,
  Box,
  Dialog,
  DialogContent,
  DialogTitle,
  Divider,
  Typography,
  styled,
} from "@mui/material";
import { ExpandMore } from "@mui/icons-material";

interface SourceItemDetailsProps {
  open: boolean;
  onClose: () => void;
  item: { article: SourceItem; analysis?: ArticleAnalysis };
}

const StyledAccordionSummary = styled(AccordionSummary)<AccordionSummaryProps>(
  ({ theme }) => ({
    "&.Mui-expanded": {
      backgroundColor: theme.palette.primary.dark,
      color: theme.palette.primary.contrastText,
    },
    "&:hover": {
      backgroundColor: theme.palette.primary.light,
      color: theme.palette.primary.contrastText,
    },
  }),
);

const SourceItemDetails: FC<SourceItemDetailsProps> = ({
  open,
  item,
  onClose,
}) => {
  return (
    <Dialog scroll="paper" open={open} onClose={onClose}>
      <DialogTitle>Source Item Analysis</DialogTitle>
      <DialogContent>
        <Accordion>
          <StyledAccordionSummary expandIcon={<ExpandMore />}>
            Article Content
          </StyledAccordionSummary>
          <AccordionDetails>
            <Box>
              <Typography variant="h5">{item.article.title}</Typography>
              <Divider sx={(theme) => ({ my: theme.spacing(1) })} />
              <Typography variant="subtitle1">
                {item.article.content}
              </Typography>
            </Box>
          </AccordionDetails>
        </Accordion>
        <Accordion>
          <StyledAccordionSummary expandIcon={<ExpandMore />}>
            Article Analysis
          </StyledAccordionSummary>
          <AccordionDetails>
            <BaseAnalysisSection articleAnalysis={item.analysis} />
          </AccordionDetails>
        </Accordion>
        <Accordion>
          <StyledAccordionSummary expandIcon={<ExpandMore />}>
            Article Counter Analysis
          </StyledAccordionSummary>
          <AccordionDetails>
            <CounterAnalysisSection articleAnalysis={item.analysis} />
          </AccordionDetails>
        </Accordion>
      </DialogContent>
    </Dialog>
  );
};

export { SourceItemDetails, SourceItemDetailsProps };
