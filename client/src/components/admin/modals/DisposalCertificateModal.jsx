import React from 'react';
import { 
  X, 
  Shield, 
  FileText, 
  Calendar, 
  User, 
  Hash, 
  CheckCircle,
  AlertTriangle,
  Clock,
  ExternalLink,
  Copy
} from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { toast } from 'react-hot-toast';

const DisposalCertificateModal = ({ 
  certificate, 
  isOpen, 
  onClose, 
  onVerify,
  onValidateOTS,
  userRole 
}) => {
  if (!isOpen || !certificate) return null;
  
  const handleCopyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text)
      .then(() => toast.success(`${label} copied to clipboard`))
      .catch(() => toast.error('Failed to copy'));
  };
  
  const handleVerify = () => {
    onVerify(certificate._id);
    onClose();
  };
  
  const handleValidateOTS = () => {
    onValidateOTS(certificate._id);
  };
  
  const getMethodColor = (method) => {
    const colors = {
      'SHRED': 'bg-red-100 text-red-800',
      'ARCHIVE': 'bg-blue-100 text-blue-800',
      'DELETE': 'bg-gray-100 text-gray-800',
      'ANONYMIZE': 'bg-purple-100 text-purple-800',
      'ENCRYPT': 'bg-indigo-100 text-indigo-800'
    };
    return colors[method] || 'bg-gray-100 text-gray-800';
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b">
          <div className="flex items-center gap-3">
            <Shield className="h-6 w-6 text-blue-600" />
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                Disposal Certificate Details
              </h2>
              <p className="text-sm text-gray-600">
                {certificate.certificateId}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>
        
        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {/* Certificate Header */}
          <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {certificate.targetModel} Disposal Certificate
                </h3>
                <p className="text-sm text-gray-600">
                  Created {format(parseISO(certificate.timestamp), 'PPpp')}
                </p>
              </div>
              <div className={`px-3 py-1 rounded-full text-sm font-bold ${getMethodColor(certificate.disposalMethod)}`}>
                {certificate.disposalMethod}
              </div>
            </div>
          </div>
          
          {/* Grid Layout */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Column - Certificate Details */}
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  Certificate Information
                </h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Certificate ID:</span>
                    <div className="flex items-center gap-2">
                      <code className="text-sm font-mono text-gray-900">
                        {certificate.certificateId}
                      </code>
                      <button
                        onClick={() => handleCopyToClipboard(certificate.certificateId, 'Certificate ID')}
                        className="p-1 hover:bg-gray-200 rounded"
                      >
                        <Copy className="h-3 w-3 text-gray-500" />
                      </button>
                    </div>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Tenant:</span>
                    <span className="text-sm font-medium text-gray-900">
                      {certificate.tenantId}
                    </span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Model Type:</span>
                    <span className="text-sm font-medium text-gray-900">
                      {certificate.targetModel}
                    </span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Disposal Reason:</span>
                    <span className="text-sm font-medium text-gray-900">
                      {certificate.disposalReason || 'Retention period expired'}
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Compliance Information */}
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <h4 className="font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <Shield className="h-4 w-4 text-green-600" />
                  Compliance References
                </h4>
                <ul className="space-y-1">
                  {certificate.complianceReferences?.map((ref, idx) => (
                    <li key={idx} className="text-sm text-gray-700">
                      • {ref}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            
            {/* Right Column - Audit & Verification */}
            <div className="space-y-4">
              {/* Audit Trail */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Audit Trail
                </h4>
                <div className="space-y-3">
                  <div>
                    <div className="text-xs text-gray-500">Created</div>
                    <div className="text-sm text-gray-900 flex items-center gap-2">
                      {format(parseISO(certificate.timestamp), 'PPpp')}
                      {certificate.disposedBy && (
                        <span className="text-xs text-gray-600">
                          by {certificate.disposedBy}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {certificate.verificationTimestamp && (
                    <div>
                      <div className="text-xs text-gray-500">Verified</div>
                      <div className="text-sm text-gray-900 flex items-center gap-2">
                        {format(parseISO(certificate.verificationTimestamp), 'PPpp')}
                        {certificate.verifiedBy && (
                          <span className="text-xs text-gray-600">
                            by {certificate.verifiedBy}
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Security Information */}
              <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                <h4 className="font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <Hash className="h-4 w-4 text-purple-600" />
                  Security & Integrity
                </h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Certificate Hash:</span>
                    <div className="flex items-center gap-2">
                      <code className="text-xs font-mono text-gray-900 truncate max-w-[150px]">
                        {certificate.certificateHash}
                      </code>
                      <button
                        onClick={() => handleCopyToClipboard(certificate.certificateHash, 'Hash')}
                        className="p-1 hover:bg-purple-100 rounded"
                      >
                        <Copy className="h-3 w-3 text-gray-500" />
                      </button>
                    </div>
                  </div>
                  
                  {certificate.otsProof && (
                    <div>
                      <div className="text-sm text-gray-600 mb-1">OTS Proof:</div>
                      <div className="flex items-center gap-2">
                        <code className="text-xs font-mono text-gray-900 bg-white p-2 rounded border truncate flex-1">
                          {certificate.otsProof.substring(0, 40)}...
                        </code>
                        <button
                          onClick={handleValidateOTS}
                          className="px-3 py-1 bg-purple-100 text-purple-700 rounded text-sm hover:bg-purple-200 flex items-center gap-1"
                        >
                          <ExternalLink className="h-3 w-3" />
                          Validate
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
          
          {/* Status Summary */}
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {certificate.verified ? (
                  <div className="flex items-center gap-2 text-green-700">
                    <CheckCircle className="h-5 w-5" />
                    <span className="font-medium">Verified and Compliant</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-yellow-700">
                    <Clock className="h-5 w-5" />
                    <span className="font-medium">Pending Verification</span>
                  </div>
                )}
                
                {certificate.legalHold && (
                  <div className="flex items-center gap-2 text-red-700">
                    <AlertTriangle className="h-5 w-5" />
                    <span className="font-medium">Legal Hold Applied</span>
                  </div>
                )}
              </div>
              
              <div className="text-sm text-gray-600">
                {certificate.verified ? 
                  'Ready for audit' : 
                  'Requires manual verification'}
              </div>
            </div>
          </div>
        </div>
        
        {/* Footer Actions */}
        <div className="p-6 border-t bg-gray-50 flex justify-between">
          <div className="text-sm text-gray-600">
            This certificate is part of the permanent disposal ledger
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Close
            </button>
            
            {!certificate.verified && userRole !== 'viewer' && (
              <button
                onClick={handleVerify}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
              >
                <CheckCircle className="h-4 w-4" />
                Mark as Verified
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DisposalCertificateModal;
