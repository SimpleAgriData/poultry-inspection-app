import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
	return {
		name: "SiAD Stallkarte App",
		short_name: "Stallkarte",
		description: "Simple Agri Data Stallkarte App",
		start_url: "/",
		display: "standalone",
		background_color: "#ffffff",
		theme_color: "#2a6a47",
		icons: [
			{
				src: "/web-app-manifest-192x192.png",
				sizes: "192x192",
				type: "image/png",
				purpose: "maskable",
			},
			{
				src: "/web-app-manifest-512x512.png",
				sizes: "512x512",
				type: "image/png",
				purpose: "maskable",
			},
		],
	};
}
