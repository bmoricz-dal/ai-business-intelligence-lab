import type { Metadata } from "next";
import { headers } from "next/headers";
import "./globals.css";

const title = "DAL Data & AI Lab | UK SME AI Adoption Intelligence";
const description =
  "Independent, evidence-led research on how UK SMEs use, integrate and govern AI, with sector studies and practical adoption pathways.";

export async function generateMetadata(): Promise<Metadata> {
  const requestHeaders = await headers();
  const host =
    requestHeaders.get("x-forwarded-host") ?? requestHeaders.get("host");
  const protocol =
    requestHeaders.get("x-forwarded-proto") ??
    (host?.startsWith("localhost") ? "http" : "https");
  const imageUrl = host ? `${protocol}://${host}/og.png` : undefined;

  return {
    title,
    description,
    icons: {
      icon: [
        { url: "/icon.svg?v=dal-music-2", type: "image/svg+xml" },
        { url: "/favicon.svg?v=dal-music-2", type: "image/svg+xml" },
      ],
      shortcut: "/icon.svg?v=dal-music-2",
    },
    openGraph: {
      type: "website",
      title,
      description,
      images: imageUrl
        ? [{ url: imageUrl, width: 1734, height: 907, alt: "DAL Data & AI Lab — UK SME AI Adoption Intelligence" }]
        : [],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: imageUrl ? [imageUrl] : [],
    },
  };
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
