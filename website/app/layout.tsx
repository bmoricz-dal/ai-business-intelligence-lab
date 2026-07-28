import type { Metadata } from "next";
import { headers } from "next/headers";
import "./globals.css";

const title = "UK SME AI Adoption Insights | SME Intelligence Lab";
const description =
  "A growing evidence base on AI use, integration, governance, sectors and adoption pathways among UK businesses.";

export async function generateMetadata(): Promise<Metadata> {
  const requestHeaders = await headers();
  const host =
    requestHeaders.get("x-forwarded-host") ?? requestHeaders.get("host");
  const protocol =
    requestHeaders.get("x-forwarded-proto") ??
    (host?.startsWith("localhost") ? "http" : "https");
  const imageUrl = host ? `${protocol}://${host}/og-light.png` : undefined;

  return {
    title,
    description,
    icons: {
      icon: "/favicon.svg",
      shortcut: "/favicon.svg",
    },
    openGraph: {
      type: "website",
      title,
      description,
      images: imageUrl
        ? [{ url: imageUrl, width: 1734, height: 907, alt: "UK SME AI Adoption Insights" }]
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
