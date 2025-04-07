import React from "react";
import axios from "axios";
import { Flex, IconButton, Tooltip } from "@radix-ui/themes";

function PdfUpload({
  setResponse,
  targetLanguage,
  setDocumentReady,
}: {
  setResponse: (data: any) => void;
  targetLanguage: string;
  setDocumentReady: (ready: boolean) => void;
}) {
  const handleUpload = async (
    e: React.ChangeEvent<HTMLInputElement>,
    type: "summarize" | "translate"
  ) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];

      const formData = new FormData();
      formData.append("file", selectedFile);
      if (type === "translate") {
        formData.append("target_language", targetLanguage);
      }

      const route = type === "summarize" ? "summarize" : "translatedoc";

      try {
        const response = await axios.post(
          `http://127.0.0.1:5000/${route}`,
          formData,
          { headers: { "Content-Type": "multipart/form-data" } }
        );

        setResponse(response.data);
        setDocumentReady(true);
      } catch (error) {
        console.error(`Error uploading file to ${route}:`, error);
      }
    }
  };

  return (
    <Flex gap="4" mt="4">
      {/* Summarize Upload */}
      <Tooltip content="Upload PDF to Summarize">
        <label>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => handleUpload(e, "summarize")}
            style={{ display: "none" }}
          />
          <IconButton
            variant="soft"
            size="3"
            className="rounded-full border border-black"
            asChild
          >
            <span>
              <i className="fas fa-folder" style={{ fontSize: "18px" }}></i>
            </span>
          </IconButton>
        </label>
      </Tooltip>

      {/* Translate Upload */}
      <Tooltip content="Upload PDF to Translate">
        <label>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => handleUpload(e, "translate")}
            style={{ display: "none" }}
          />
          <IconButton
            variant="soft"
            size="3"
            className="rounded-full border border-black"
            asChild
          >
            <span>
              <i className="fas fa-globe" style={{ fontSize: "18px" }}></i>
            </span>
          </IconButton>
        </label>
      </Tooltip>
    </Flex>
  );
}

export default PdfUpload;
