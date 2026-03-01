"use client"

import { useState, useCallback } from "react"
import { motion } from "framer-motion"
import { Upload, Flame, Github, Check } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"

const stats = [
  { value: "97%", label: "Accuracy Rate" },
  { value: "3", label: "AI Models" },
  { value: "50ms", label: "Avg Response" },
  { value: "10K+", label: "Images Analyzed" },
]

const modelTags = [
  { name: "GPT-4V", icon: "🧠" },
  { name: "Gemini", icon: "✨" },
  { name: "Claude", icon: "🎭" },
]

export function Hero() {
  const [uploadState, setUploadState] = useState<"idle" | "uploading" | "complete">("idle")
  const [dragOver, setDragOver] = useState(false)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const files = e.dataTransfer.files
    if (files.length) {
      handleFile(files[0])
    }
  }, [])

  const handleFile = (file: File) => {
    setUploadState("uploading")
    setTimeout(() => {
      setUploadState("complete")
    }, 2000)
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      handleFile(e.target.files[0])
    }
  }

  return (
    <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-secondary border border-border/50 text-sm font-medium text-primary mb-8 hover:border-primary/50 transition-colors cursor-default">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              Powered by OpenAI + Gemini + Anthropic
            </div>
          </motion.div>

          {/* Heading */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-4xl sm:text-5xl lg:text-7xl font-bold tracking-tight mb-6"
          >
            Detect AI-Generated
            <br />
            <span className="text-gradient">Images & Videos</span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10"
          >
            Multi-model AI detection engine that combines GPT-4 Vision, Google Gemini, and Anthropic Claude 
            to verify authenticity with 97% accuracy.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-wrap justify-center gap-4 mb-16"
          >
            <Button variant="gradient" size="lg" className="gap-2">
              <Flame className="w-5 h-5" />
              Try Free Demo
            </Button>
            <Button variant="outline" size="lg" className="gap-2" asChild>
              <Link href="https://github.com/josecookai/fakephoto-ai" target="_blank">
                <Github className="w-5 h-5" />
                View on GitHub
              </Link>
            </Button>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="flex flex-wrap justify-center gap-8 sm:gap-16 mb-20"
          >
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl sm:text-4xl font-bold text-gradient">{stat.value}</div>
                <div className="text-sm text-muted-foreground mt-1">{stat.label}</div>
              </div>
            ))}
          </motion.div>

          {/* Demo Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="max-w-3xl mx-auto"
          >
            <div className="relative rounded-2xl bg-secondary/50 border border-border/50 p-6 sm:p-8 backdrop-blur-sm hover:border-primary/30 transition-colors group">
              {/* Gradient line at top */}
              <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent" />
              
              {/* Header */}
              <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
                <h3 className="text-lg font-semibold">Live Detection Demo</h3>
                <div className="flex flex-wrap gap-2">
                  {modelTags.map((tag) => (
                    <span
                      key={tag.name}
                      className="px-3 py-1 rounded-full text-xs font-medium bg-secondary text-muted-foreground hover:bg-gradient-to-r hover:from-indigo-500 hover:to-purple-600 hover:text-white transition-all cursor-default"
                    >
                      {tag.icon} {tag.name}
                    </span>
                  ))}
                </div>
              </div>

              {/* Upload Zone */}
              <div
                onClick={() => document.getElementById("file-input")?.click()}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-xl p-12 sm:p-16 text-center cursor-pointer transition-all duration-300 ${
                  dragOver
                    ? "border-primary bg-primary/5 scale-[1.02]"
                    : "border-border hover:border-primary/50 hover:bg-secondary/50"
                }`}
              >
                <input
                  type="file"
                  id="file-input"
                  accept="image/*,video/*"
                  className="hidden"
                  onChange={handleFileInput}
                />

                {uploadState === "idle" && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="animate-float"
                  >
                    <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-primary/25">
                      <Upload className="w-10 h-10" />
                    </div>
                    <h4 className="text-lg font-semibold mb-2">Drop your image or video here</h4>
                    <p className="text-sm text-muted-foreground">
                      Supports JPG, PNG, WebP, MP4, MOV • Max 100MB
                    </p>
                  </motion.div>
                )}

                {uploadState === "uploading" && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                  >
                    <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white">
                      <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    </div>
                    <h4 className="text-lg font-semibold mb-2">Analyzing...</h4>
                    <p className="text-sm text-muted-foreground">Processing with 3 AI models</p>
                  </motion.div>
                )}

                {uploadState === "complete" && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    onClick={(e) => {
                      e.stopPropagation()
                      setUploadState("idle")
                    }}
                  >
                    <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center text-white">
                      <Check className="w-10 h-10" />
                    </div>
                    <h4 className="text-lg font-semibold mb-2 text-green-500">Likely Authentic</h4>
                    <p className="text-sm text-muted-foreground">92% Confidence • Click to analyze another</p>
                  </motion.div>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}