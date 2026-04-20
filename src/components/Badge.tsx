import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../utils/cn.js";

/**
 * Badge — compact status/label chip. Uses the shared semantic tokens,
 * so each brand's "success" / "warning" inherit status hues from
 * tokens/colors.ts rather than brand primary.
 */
const badgeVariants = cva(
  [
    "inline-flex items-center gap-1 rounded-pill border px-2.5 py-0.5",
    "text-xs font-medium transition-colors",
    "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  ].join(" "),
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground hover:bg-primary/80",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        accent:
          "border-transparent bg-accent text-accent-foreground hover:bg-accent/80",
        outline: "text-foreground border-border",
        success:
          "border-transparent bg-emerald-100 text-emerald-900 dark:bg-emerald-900/30 dark:text-emerald-200",
        warning:
          "border-transparent bg-amber-100 text-amber-900 dark:bg-amber-900/30 dark:text-amber-200",
        danger:
          "border-transparent bg-red-100 text-red-900 dark:bg-red-900/30 dark:text-red-200",
        info: "border-transparent bg-sky-100 text-sky-900 dark:bg-sky-900/30 dark:text-sky-200",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { badgeVariants };
