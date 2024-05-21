import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}


function xorshift(seed) {
  let x = seed || 123456789;
  let y = 362436069;
  let z = 521288629;
  let w = 88675123;

  return function() {
    const t = x ^ (x << 11);
    x = y;
    y = z;
    z = w;
    w = (w ^ (w >>> 19)) ^ (t ^ (t >>> 8));
    return (w >>> 0) / 0xffffffff; // Normalize to [0, 1]
  };
}

export function getRandomColor(seed) {
  const random = xorshift(seed);

  // Convert the normalized random value to a hexadecimal color
  const color = Math.floor(random() * 0xFFFFFF).toString(16).padStart(6, '0');

  return `#${color}`;
}