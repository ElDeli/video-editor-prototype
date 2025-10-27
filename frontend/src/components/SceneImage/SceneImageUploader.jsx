import { useState } from 'react'
import { Image, Upload, X, Loader } from 'lucide-react'
import axios from 'axios'

const API_BASE = '/api'

export default function SceneImageUploader({ scene, onUpdate }) {
    const [showModal, setShowModal] = useState(false)
    const [uploading, setUploading] = useState(false)

    const currentImage = scene.background_type === 'image' ? scene.background_value : null

    const handleFileUpload = async (e) => {
        const file = e.target.files?.[0]
        if (!file) return

        setUploading(true)
        try {
            const formData = new FormData()
            formData.append('file', file)

            const response = await axios.post(`${API_BASE}/uploads/image`, formData)

            // Update scene with uploaded image path
            await axios.put(`${API_BASE}/scenes/${scene.id}`, {
                background_type: 'image',
                background_value: response.data.path
            })

            onUpdate?.()
            setShowModal(false)
            alert('Image uploaded successfully!')
        } catch (error) {
            console.error('Upload error:', error)
            alert(error.response?.data?.error || 'Failed to upload image')
        } finally {
            setUploading(false)
        }
    }

    const removeImage = async () => {
        try {
            await axios.put(`${API_BASE}/scenes/${scene.id}`, {
                background_type: 'solid',
                background_value: '#000000'
            })
            onUpdate?.()
        } catch (error) {
            console.error('Remove error:', error)
            alert('Failed to remove image')
        }
    }

    return (
        <>
            {/* Trigger Button */}
            <button
                onClick={(e) => {
                    e.stopPropagation()
                    setShowModal(true)
                }}
                className={`flex items-center gap-1 px-2 py-1 rounded text-xs ${
                    currentImage
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
                title="Upload custom image"
            >
                <Image className="w-3 h-3" />
                {currentImage ? 'Custom' : 'Upload'}
            </button>

            {currentImage && (
                <button
                    onClick={(e) => {
                        e.stopPropagation()
                        removeImage()
                    }}
                    className="p-1 bg-red-600 hover:bg-red-700 rounded text-white"
                    title="Remove custom image"
                >
                    <X className="w-3 h-3" />
                </button>
            )}

            {/* Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
                    <div className="bg-darker rounded-lg w-full max-w-2xl overflow-hidden flex flex-col">
                        {/* Header */}
                        <div className="flex items-center justify-between p-4 border-b border-gray-700">
                            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                                <Image className="w-6 h-6" />
                                Upload Scene Image
                            </h2>
                            <button
                                onClick={() => setShowModal(false)}
                                className="p-2 hover:bg-gray-700 rounded"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Content */}
                        <div className="p-6">
                            <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center">
                                <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                                <p className="text-gray-300 mb-4">
                                    Upload a custom background image for this scene
                                </p>
                                <p className="text-xs text-gray-500 mb-4">
                                    Supported formats: JPG, PNG, WEBP (Max 10MB)
                                </p>
                                <input
                                    type="file"
                                    accept=".jpg,.jpeg,.png,.webp"
                                    onChange={handleFileUpload}
                                    disabled={uploading}
                                    className="hidden"
                                    id={`image-upload-${scene.id}`}
                                />
                                <label
                                    htmlFor={`image-upload-${scene.id}`}
                                    className={`inline-block px-6 py-3 rounded cursor-pointer ${
                                        uploading
                                            ? 'bg-gray-600 text-gray-400'
                                            : 'bg-primary hover:bg-primary-dark text-white'
                                    }`}
                                >
                                    {uploading ? (
                                        <span className="flex items-center gap-2">
                                            <Loader className="w-4 h-4 animate-spin" />
                                            Uploading...
                                        </span>
                                    ) : (
                                        'Choose Image'
                                    )}
                                </label>
                            </div>

                            {/* Current Image Preview */}
                            {currentImage && (
                                <div className="mt-4 p-4 bg-gray-800 rounded">
                                    <p className="text-sm text-gray-400 mb-2">Current Image:</p>
                                    <p className="text-xs text-gray-500 break-all">{currentImage}</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </>
    )
}
