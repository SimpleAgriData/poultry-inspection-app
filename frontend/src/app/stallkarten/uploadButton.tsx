"use client";
import Button from "@/components/button";
import { InfoBanner } from "@/components/info-banner";
import { useShallowStallkarten } from "@/contexts/ShallowStallkartenContext";
import { apiService } from "@/services/api/service";

import { useRef, useState } from "react";
import { MdUpload } from "react-icons/md";

type ImportError = {
    code: string;
    message: string;
    german_display_message?: string;
};

type ImportErrorResponse = {
    error: ImportError;
};

export function UploadStallkarteButton() {
    const inputRef = useRef<HTMLInputElement>(null);
    const [importError, setImportError] = useState<ImportError | null>(null);
    const [importState, setImportState] = useState<"idle" | "uploading" | "success" | "error">("idle");
    const [importedFileName, setImportedFileName] = useState<string | null>(null);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const [displayErrorMessage, setDisplayErrorMessage] = useState<boolean>(false);
    
    const { refetch: refetchStallkarten } = useShallowStallkarten();
    function openFilePicker() {
        inputRef.current?.click();
    }

    async function handleFileChange(
        event: React.ChangeEvent<HTMLInputElement>,
    ) {
        setErrorMessage(null);
        setDisplayErrorMessage(false);
        setImportedFileName(event.target.files?.[0]?.name || null);

        const file = event.target.files?.[0];
        if (!file) return;

        setImportError(null);
        setImportState("uploading");

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response =
                await apiService.stallkarte.importStallkarte(formData);
            

            if (!response.ok) {
                const errorResponse = (await response.json()) as ImportErrorResponse;

                setImportError({
                    code: errorResponse.error.code,
                    message: errorResponse.error.message,
                    german_display_message:
                        errorResponse.error.german_display_message,
                });
                setErrorMessage(errorResponse.error.german_display_message || errorResponse.error.message);
                setDisplayErrorMessage(true);
                setImportState("error");

                setTimeout(() => {
                    setImportState("idle");
                }, 5000);

                return;
            }
            const blob = await response.blob();
            console.log(blob);

            setImportState("success");
            
            setTimeout(async () => {
                setImportState("idle");
                await refetchStallkarten();
            }, 5000);

        } catch (error) {
            console.error("Import failed:", error);
            setImportError({
                code: "NETWORK_ERROR",
                message: "Network request failed.",
                german_display_message:
                    "Die Datei konnte nicht hochgeladen werden.",
            });

            setImportState("error");

            setTimeout(() => {
                setImportState("idle");
            }, 5000);
        } finally {
            event.target.value = "";
        }

    }

    return (
        <>
            <input
                ref={inputRef}
                type="file"
                accept=".xlsx"
                hidden
                onChange={handleFileChange}
            />

            <Button
                type="primary"
                iconLeft={<MdUpload size="1.5em" />}
                withLoader={importState === "uploading"}
                loaderPosition="left"
                disabled={importState === "uploading"}
                onClick={openFilePicker}
            >
                {importState !== "uploading" && "Stallkarte hochladen"}
                {importState === "uploading" && "Hochladen..."}
            </Button>
            {importState === "success" && (
                <InfoBanner icon="auto" type="info" align="left">
                    Upload erfolgreich!
                </InfoBanner>
            )}
            {displayErrorMessage && (
                <InfoBanner icon="auto" type="error" align="left">
                    <p><b>Upload-Fehler:</b> {errorMessage || "Unbekannter Fehler."}</p>
                </InfoBanner>
            )}
        </>
    );
}
export default UploadStallkarteButton;