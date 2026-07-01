"use client";

import React from "react";
import { motion } from "framer-motion";
import { UploadCloud, Search, Scale, ShieldCheck, FileCheck, ArrowRight, ArrowDown } from "lucide-react";

interface Step {
  id: number;
  label: string;
  sublabel: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  glow: string;
}

export function PipelineAnimation() {
  const steps: Step[] = [
    {
      id: 1,
      label: "PDF Upload",
      sublabel: "Upload legal judgments",
      icon: UploadCloud,
      color: "bg-blue-500 text-blue-500",
      glow: "shadow-blue-500/20",
    },
    {
      id: 2,
      label: "Research Agent",
      sublabel: "Extract statutes & precedents",
      icon: Search,
      color: "bg-violet-500 text-violet-500",
      glow: "shadow-violet-500/20",
    },
    {
      id: 3,
      label: "Case Analysis Agent",
      sublabel: "Synthesize issues & rulings",
      icon: Scale,
      color: "bg-indigo-500 text-indigo-500",
      glow: "shadow-indigo-500/20",
    },
    {
      id: 4,
      label: "Verification Agent",
      sublabel: "Verify citations & detect hallucinations",
      icon: ShieldCheck,
      color: "bg-emerald-500 text-emerald-500",
      glow: "shadow-emerald-500/20",
    },
    {
      id: 5,
      label: "FIRAC Brief",
      sublabel: "Ready-to-use structured document",
      icon: FileCheck,
      color: "bg-amber-500 text-amber-500",
      glow: "shadow-amber-500/20",
    },
  ];

  return (
    <div className="w-full py-12">
      {/* Desktop Pipeline (Horizontal) */}
      <div className="hidden lg:flex items-center justify-between gap-2 max-w-5xl mx-auto px-4">
        {steps.map((step, index) => {
          const Icon = step.icon;
          return (
            <React.Fragment key={step.id}>
              {/* Step Card */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.15 }}
                whileHover={{ y: -5 }}
                className={`relative flex flex-col items-center p-5 rounded-2xl border border-border bg-card text-center w-48 shadow-lg ${step.glow} transition-shadow`}
              >
                <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${step.color.split(" ")[0]}/10 ${step.color.split(" ")[1]} mb-4`}>
                  <Icon className="h-6 w-6" />
                </div>
                <h3 className="font-semibold text-sm text-foreground">{step.label}</h3>
                <p className="text-xs text-muted-foreground mt-1 leading-normal">{step.sublabel}</p>
                <div className={`absolute top-0 left-1/2 -translate-x-1/2 h-1 w-12 rounded-b-full ${step.color.split(" ")[0]}`} />
              </motion.div>

              {/* Connector */}
              {index < steps.length - 1 && (
                <div className="flex-1 relative flex items-center justify-center min-w-8">
                  {/* Background line */}
                  <div className="h-0.5 w-full bg-border" />
                  
                  {/* Glowing moving dot */}
                  <motion.div
                    className={`absolute h-2 w-2 rounded-full ${steps[index + 1].color.split(" ")[0]}`}
                    initial={{ left: "0%" }}
                    animate={{ left: "100%" }}
                    transition={{
                      repeat: Infinity,
                      duration: 2,
                      delay: index * 0.4,
                      ease: "easeInOut",
                    }}
                  />
                  <ArrowRight className="absolute right-0 h-4 w-4 text-muted-foreground/60" />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Mobile/Tablet Pipeline (Vertical) */}
      <div className="flex lg:hidden flex-col items-center gap-4 px-4">
        {steps.map((step, index) => {
          const Icon = step.icon;
          return (
            <React.Fragment key={step.id}>
              {/* Step Card */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className={`relative flex items-center gap-4 p-4 rounded-xl border border-border bg-card w-full max-w-md shadow-md ${step.glow}`}
              >
                <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${step.color.split(" ")[0]}/10 ${step.color.split(" ")[1]}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-sm text-foreground">{step.label}</h3>
                  <p className="text-xs text-muted-foreground leading-normal mt-0.5">{step.sublabel}</p>
                </div>
                <div className={`absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 rounded-r-full ${step.color.split(" ")[0]}`} />
              </motion.div>

              {/* Connector */}
              {index < steps.length - 1 && (
                <div className="relative flex flex-col items-center h-8 justify-center">
                  <div className="w-0.5 h-full bg-border" />
                  <motion.div
                    className={`absolute w-1.5 h-1.5 rounded-full ${steps[index + 1].color.split(" ")[0]}`}
                    initial={{ top: "0%" }}
                    animate={{ top: "100%" }}
                    transition={{
                      repeat: Infinity,
                      duration: 1.8,
                      delay: index * 0.3,
                      ease: "easeInOut",
                    }}
                  />
                  <ArrowDown className="absolute bottom-0 h-4 w-4 text-muted-foreground/60" />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
