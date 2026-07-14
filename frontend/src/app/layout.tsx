import "./globals.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";
import App from "@/app/app";

export const metadata: Metadata = {
	title: "SiAD Stallkarte",
	description: "Simple Agri Data Stallkarte App",
	metadataBase: new URL("https://stallkarte.simple-agri-data.de"),
};

function RootLayout({
	children,
}: Readonly<{
	children: ReactNode;
}>) {
	return (
		<html lang="en">
			<body className="bg-secondary-container">
				<App>{children}</App>
			</body>
		</html>
	);
}

export default RootLayout;
