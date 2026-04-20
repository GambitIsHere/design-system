import * as React from "react";
import { cn } from "../utils/cn.js";

/**
 * Input — themed text input. Styling is minimal so consumers can
 * layer `<Label>` / error states externally.
 */
export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  invalid?: boolean;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type = "text", invalid, ...props }, ref) => {
    return (
      <input
        type={type}
        ref={ref}
        aria-invalid={invalid || undefined}
        className={cn(
          "flex h-10 w-full rounded-md border bg-background px-3 py-2 text-sm",
          "border-input text-foreground placeholder:text-muted-foreground",
          "file:border-0 file:bg-transparent file:text-sm file:font-medium",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1",
          "disabled:cursor-not-allowed disabled:opacity-50",
          invalid &&
            "border-destructive focus-visible:ring-destructive/40 text-destructive",
          className,
        )}
        {...props}
      />
    );
  },
);
Input.displayName = "Input";
