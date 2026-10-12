"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

export interface SquircleProps extends React.HTMLAttributes<HTMLDivElement> {
  cornerRadius?: number
}

export function Squircle({ className, ...props }: SquircleProps) {
  return (
    <div
      aria-hidden="true"
      className={cn(
        "absolute inset-0 -z-0 rounded-[28px] overflow-hidden pointer-events-none",
        className,
      )}
      {...props}
    />
  )
}

export default Squircle
