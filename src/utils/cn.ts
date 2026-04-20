import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Tiny className helper used across components — combines clsx's
 * conditional merging with tailwind-merge's conflict resolution so
 * consumers can safely override utilities on a wrapped component:
 *
 *   <Button className="bg-red-500" />   // wins over default bg-primary
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
