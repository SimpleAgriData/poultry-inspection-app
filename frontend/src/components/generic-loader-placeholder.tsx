import Ellipsis from "@/components/ellipsis";

interface GenericLoaderPlaceholderProps {
	height?: "full" | "auto";
	text?: string;
	withEllipsis?: boolean;
}

export default function GenericLoaderPlaceholder({
	height = "full",
	text = "Lade Daten",
	withEllipsis = true,
}: GenericLoaderPlaceholderProps) {
	const renderedText = withEllipsis ? (
		<>
			{text}
			<Ellipsis fixedWidth={true} delayMs={250} />
		</>
	) : (
		text
	);

	if (height === "full") {
		return (
			<div className="flex flex-col items-center justify-center h-full p-4">
				<p className="text-on-surface-variant">{renderedText}</p>
			</div>
		);
	}

	return (
		<div className="flex flex-col items-center p-2">
			<p className="text-on-surface-variant">{renderedText}</p>
		</div>
	);
}
