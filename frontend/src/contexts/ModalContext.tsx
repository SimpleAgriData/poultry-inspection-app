import type React from "react";
import { createContext, useContext, useState } from "react";

export interface ModalOptions {
	title?: React.ReactNode;
	body: React.ReactNode;
	footer?: React.ReactNode;
	width?: "full" | "auto";
}

export interface ModalContextType {
	showModal: (props: ModalOptions) => void;
	hideModal: () => void;
}

const ModalContext = createContext<ModalContextType | undefined>(undefined);

interface ModalProviderProps {
	children: React.ReactNode;
}

export function ModalProvider({ children }: ModalProviderProps) {
	const [content, setContent] = useState<ModalOptions | null>(null);

	const showModal = (options: ModalOptions) => {
		setContent(options);
	};

	const hideModal = () => {
		setContent(null);
	};

	return (
		<ModalContext.Provider value={{ showModal, hideModal }}>
			{children}
			{content && (
				<div className="fixed w-full inset-0 flex items-center justify-center bg-gray-950/50 backdrop-blur-xs overflow-auto gutter-stable">
					<div className={`max-w-md p-4 ${content.width === "full" ? "w-full" : "w-auto"}`}>
						<div className="bg-white rounded p-4">
							{content.title && <div className="text-xl font-semibold mb-4">{content.title}</div>}
							<div className="mb-4">{content.body}</div>
							{content.footer && <div className="mt-4">{content.footer}</div>}
						</div>
					</div>
				</div>
			)}
		</ModalContext.Provider>
	);
}

export function useModal(): ModalContextType {
	const context = useContext(ModalContext);
	if (context === undefined) {
		throw new Error("useModal must be used within a ModalProvider");
	}
	return context;
}
