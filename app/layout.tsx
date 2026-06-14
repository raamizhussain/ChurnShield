import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'ChurnShield - Real-Time Churn Intelligence Dashboard',
  description: 'Executive ROI Management & Causal Inference Platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="bg-background">
      <body className="bg-background text-foreground">
        {children}
      </body>
    </html>
  );
}
