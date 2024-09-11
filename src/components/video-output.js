import React, { useState } from 'react';
import { Search, Upload, Sliders, X } from 'lucide-react';
import placeholder1 from "../img/placeholder1.jpg";

const VideoFrameRetrieval = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedFrame, setSelectedFrame] = useState(null);

    // Mock data for demonstration
    const frames = [
        { id: 1, src: placeholder1, timestamp: '00:01:23' },
        { id: 2, src: placeholder1, timestamp: '00:02:45' },
        { id: 3, src: placeholder1, timestamp: '00:03:56' },
        { id: 4, src: placeholder1, timestamp: '00:05:12' },
    ];

    return (
        <div className="min-h-screen bg-gray-900 text-white p-8">
            <h1 className="text-3xl font-bold mb-8">Video Frame Retrieval</h1>

            {/* Search Bar */}
            <div className="mb-8 relative">
                <input
                    type="text"
                    placeholder="Search for frames..."
                    className="w-full p-4 pr-12 rounded-lg bg-gray-800 focus:ring-2 focus:ring-blue-500"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
                <Search className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400" />
            </div>

            {/* Upload Area */}
            <div className="mb-8 p-8 border-2 border-dashed border-gray-700 rounded-lg text-center">
                <Upload className="mx-auto mb-4" size={48} />
                <p>Drag and drop your video here, or click to select</p>
            </div>

            {/* Filters */}
            <div className="mb-8 flex items-center space-x-4">
                <Sliders />
                <span>Filters:</span>
                <button className="px-4 py-2 bg-blue-600 rounded-full">Time Range</button>
                <button className="px-4 py-2 bg-blue-600 rounded-full">Object Detection</button>
            </div>

            {/* Results Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {frames.map((frame) => (
                    <div
                        key={frame.id}
                        className="relative cursor-pointer"
                        onClick={() => setSelectedFrame(frame)}
                    >
                        <img src={frame.src} alt={`Frame ${frame.id}`} className="rounded-lg" />
                        <span className="absolute bottom-2 right-2 bg-black bg-opacity-50 px-2 py-1 rounded">
              {frame.timestamp}
            </span>
                    </div>
                ))}
            </div>

            {/* Modal */}
            {selectedFrame && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                    <div className="bg-gray-800 p-8 rounded-lg max-w-2xl w-full">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-2xl font-bold">Frame Details</h2>
                            <X onClick={() => setSelectedFrame(null)} className="cursor-pointer" />
                        </div>
                        <img src={selectedFrame.src} alt={`Frame ${selectedFrame.id}`} className="w-full rounded-lg mb-4" />
                        <p>Timestamp: {selectedFrame.timestamp}</p>
                        {/* Add more details as needed */}
                    </div>
                </div>
            )}
        </div>
    );
};

export default VideoFrameRetrieval;