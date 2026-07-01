import Link from "next/link";
import { Navbar } from "@/components/navbar";
import { Footer } from "@/components/footer";
import { PipelineAnimation } from "@/components/pipeline-animation";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { ShieldCheck, Scale, Compass, CheckCircle2, ChevronRight } from "lucide-react";

export default function Home() {
  const features = [
    {
      title: "Research Agent",
      description: "Automatically extracts governing statutes, constitutional provisions, and case precedents. Traces citations across pages instantly.",
      icon: Compass,
      color: "text-violet-500 bg-violet-500/10",
    },
    {
      title: "Case Analysis Agent",
      description: "Synthesizes facts, defines core legal issues, analyses reasoning, and summarizes holdings into a precise draft brief.",
      icon: Scale,
      color: "text-indigo-500 bg-indigo-500/10",
    },
    {
      title: "Verification Agent",
      description: "Performs rigorous cross-referencing to check for model hallucinations and flags incorrect or missing citations.",
      icon: ShieldCheck,
      color: "text-emerald-500 bg-emerald-500/10",
    },
  ];

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />

      {/* Main Container */}
      <main className="flex-1 flex flex-col justify-center">
        {/* Hero Section */}
        <section className="relative overflow-hidden py-20 lg:py-28 bg-gradient-to-b from-zinc-50/50 to-transparent dark:from-zinc-950/20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
            
            {/* Tagline Badge */}
            <div className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1.5 text-xs font-semibold text-primary mb-6 animate-pulse">
              <Scale className="h-3.5 w-3.5" />
              AI Multi-Agent Legal Research Platform
            </div>

            {/* Hero Heading */}
            <h1 className="mx-auto max-w-4xl text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl lg:text-6xl leading-[1.15]">
              Synthesize Complex Legal Judgments with{" "}
              <span className="bg-gradient-to-r from-violet-600 via-indigo-600 to-blue-500 bg-clip-text text-transparent dark:from-violet-400 dark:via-indigo-400 dark:to-blue-400">
                Multi-Agent Intelligence
              </span>
            </h1>

            {/* Sub-heading */}
            <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground leading-relaxed sm:text-xl">
              LexAgent orchestrates a specialized pipeline of autonomous legal agents to research, analyze, and verify court judgments, producing a structured, citation-verified FIRAC brief.
            </p>

            {/* CTA Buttons */}
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/analyzer">
                <Button size="lg" className="rounded-xl px-8 font-medium h-12 text-base shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 transition-all gap-2">
                  Launch Analyzer Workspace
                  <ChevronRight className="h-4.5 w-4.5" />
                </Button>
              </Link>
              <a
                href="#how-it-works"
                className="text-sm font-semibold leading-6 text-foreground hover:text-primary transition-colors flex items-center gap-1"
              >
                Learn how it works <span aria-hidden="true">↓</span>
              </a>
            </div>
          </div>
        </section>

        {/* Workflow Visualization Section */}
        <section id="how-it-works" className="py-16 border-y border-border bg-zinc-50/30 dark:bg-zinc-950/10">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              The Multi-Agent Workflow Pipeline
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-sm sm:text-base text-muted-foreground leading-relaxed">
              Unlike static chatbots, LexAgent runs a sequential collaborative pipeline of specialized LLM agents.
            </p>
            <PipelineAnimation />
          </div>
        </section>

        {/* Feature Highlights Section */}
        <section className="py-20 lg:py-28">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
                Built for High-Precision Legal Workflows
              </h2>
              <p className="mx-auto mt-4 max-w-2xl text-base text-muted-foreground leading-relaxed">
                Legal briefs require absolute accuracy. Our agents are structured to enforce validation, cross-check reference indices, and guarantee source grounding.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
              {features.map((feature, idx) => {
                const Icon = feature.icon;
                return (
                  <Card key={idx} className="rounded-2xl border border-border bg-card shadow-sm hover:shadow-md transition-shadow">
                    <CardHeader className="flex flex-col gap-4">
                      <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${feature.color}`}>
                        <Icon className="h-6 w-6" />
                      </div>
                      <div>
                        <CardTitle className="text-lg font-bold">{feature.title}</CardTitle>
                        <CardDescription className="mt-2 text-sm text-muted-foreground leading-relaxed">
                          {feature.description}
                        </CardDescription>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <ul className="space-y-2">
                        <li className="flex items-center gap-2 text-xs text-muted-foreground">
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                          Context-grounded analysis
                        </li>
                        <li className="flex items-center gap-2 text-xs text-muted-foreground">
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                          Zero hallucination checking
                        </li>
                      </ul>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
