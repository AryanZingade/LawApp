import React, { useState } from "react";
import TitleArea from "./components/TitleArea";
import TextInput from "./components/TextInput";
import PdfUpload from "./components/UploadDocSum";
import ResponseBox from "./components/ResponseBox";
import Translate from "./components/TranslateDrop";
import DocumentDownload from "./components/DocumentDownload";

function App() {
  const [response, setResponse] = useState<any>(null);
  const [targetLanguage, setTargetLanguage] = useState("en");
  const [documentReady, setDocumentReady] = useState(false); // Track document readiness

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        minHeight: "100vh",
        textAlign: "center",
      }}
    >
      <TitleArea />
      <TextInput setResponse={setResponse} />
      <Translate
        targetLanguage={targetLanguage}
        setTargetLanguage={setTargetLanguage}
      />

      {/* Pass setDocumentReady to PdfUpload */}
      <PdfUpload
        setResponse={setResponse}
        targetLanguage={targetLanguage}
        setDocumentReady={setDocumentReady}
      />

      {response && <ResponseBox response={response} />}

      {/* Show Download button only if document is ready */}
      {documentReady && <DocumentDownload />}
    </div>
  );
}

export default App;
