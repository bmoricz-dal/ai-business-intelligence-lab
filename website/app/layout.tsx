import type { Metadata } from "next";
import { headers } from "next/headers";
import { EditorialExperience } from "./editorial-experience";
import "./globals.css";

const title = "DAL Data & AI Lab | UK SME AI Adoption Intelligence";
const description =
  "Decision-ready intelligence on how UK SMEs use, integrate and govern AI, with sector evidence and practical implementation labs.";

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
        ? [{ url: imageUrl, width: 1662, height: 946, alt: "DAL Data & AI Lab — UK SME AI Adoption Intelligence" }]
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
      <body>
        <EditorialExperience />
        {children}
      </body>
    </html>
  );
}
