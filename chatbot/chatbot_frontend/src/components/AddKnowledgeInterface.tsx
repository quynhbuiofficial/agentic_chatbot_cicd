import { Bot, FileUp } from "lucide-react";

const AddKnowledgeInterface = () => {
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === "application/pdf") {
      // Handle PDF file upload
      console.log("PDF file selected:", file);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <div className="py-5 px-6 bg-white shadow-[0_1px_3px_0_rgb(0,0,0,0.05)] relative z-10">
        <div className="max-w-3xl mx-auto flex items-center">
          <div className="flex items-center gap-4">
            <Bot size={40} className="text-indigo-600" />
            <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-indigo-500 bg-clip-text text-transparent">
              Add Knowledge
            </h1>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto bg-gray-50">
        <div className="max-w-3xl mx-auto py-8 px-4">
          {/* Upload Section */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Upload Documents</h2>
            <p className="text-gray-600 mb-6">
              Upload PDF documents to add to the chatbot's knowledge base. The content will be processed and made available for the chatbot to use in responses.
            </p>
            
            {/* Upload Area */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-300 transition-colors">
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                className="hidden"
                id="pdf-upload"
                multiple
              />
              <label
                htmlFor="pdf-upload"
                className="cursor-pointer"
              >
                <FileUp size={40} className="mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600 mb-2">Drag and drop your PDF files here</p>
                <p className="text-sm text-gray-500 mb-4">or</p>
                <button className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
                  Browse Files
                </button>
              </label>
            </div>

            {/* Upload Requirements */}
            <div className="mt-6">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Requirements:</h3>
              <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside">
                <li>Only PDF files are supported</li>
                <li>Maximum file size: 10MB</li>
                <li>Text must be extractable from the PDF</li>
              </ul>
            </div>
          </div>

          {/* Processing Status */}
          <div className="mt-6 bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Processing Status</h2>
            <div className="text-gray-600">
              No documents are currently being processed.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AddKnowledgeInterface; 