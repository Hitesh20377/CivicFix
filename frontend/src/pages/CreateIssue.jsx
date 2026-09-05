import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowLeft, Upload, MapPin, AlertCircle } from 'lucide-react';
import api from '../services/api';

const CreateIssue = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [categories, setCategories] = useState([]);
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [image, setImage] = useState(null);
  
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch categories
    api.get('/issues/categories')
      .then(res => {
        if (res.data && res.data.data) {
          setCategories(res.data.data);
        }
      })
      .catch(err => {
        console.error("Error fetching categories:", err);
        setError("Failed to load issue categories.");
      });
  }, []);

  const handleImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setImage(e.target.files[0]);
    }
  };

  const handleGetLocation = () => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        position => {
          setLatitude(position.coords.latitude.toFixed(6));
          setLongitude(position.coords.longitude.toFixed(6));
        },
        err => {
          setError("Failed to get location: " + err.message);
        }
      );
    } else {
      setError("Geolocation is not supported by your browser");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!title || !description || !categoryId || !latitude || !longitude) {
      setError('Please fill out all required fields.');
      return;
    }

    setLoading(true);
    
    try {
      // 1. Create the issue
      const issueData = {
        title,
        description,
        category_id: parseInt(categoryId),
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude)
      };
      
      const res = await api.post('/issues', issueData);
      const newIssue = res.data.data;
      
      // 2. Upload image if selected
      if (image && newIssue.id) {
        const formData = new FormData();
        formData.append('file', image);
        
        await api.post(`/issues/${newIssue.id}/attachments`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      }
      
      // Navigate to dashboard or detail page
      navigate(`/issues`);
    } catch (err) {
      console.error("Failed to create issue:", err);
      if (err.response && err.response.data && err.response.data.errors) {
        setError("Validation error: " + JSON.stringify(err.response.data.errors));
      } else {
        setError('Failed to create issue. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <nav className="bg-white border-b border-slate-200 px-6 py-4 flex justify-between items-center sticky top-0 z-10 shadow-sm">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/issues')} className="text-slate-500 hover:text-slate-800 transition-colors">
            <ArrowLeft size={24} />
          </button>
          <h1 className="text-xl font-bold text-slate-800">Report a New Issue</h1>
        </div>
      </nav>

      <main className="flex-1 max-w-3xl w-full mx-auto p-6">
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
          {error && (
            <div className="bg-red-50 text-red-700 p-4 rounded-xl mb-6 flex items-start gap-3 border border-red-100">
              <AlertCircle className="mt-0.5" size={20} />
              <p className="text-sm font-medium">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Issue Title</label>
              <input
                type="text"
                required
                className="w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Pothole on Main Street"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Category</label>
              <select
                required
                className="w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white"
                value={categoryId}
                onChange={(e) => setCategoryId(e.target.value)}
              >
                <option value="" disabled>Select a category</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Description</label>
              <textarea
                required
                rows={4}
                className="w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Please describe the issue in detail..."
              ></textarea>
            </div>

            <div className="pt-2">
              <label className="block text-sm font-semibold text-slate-700 mb-2">Location</label>
              <div className="flex gap-4 items-center">
                <div className="flex-1">
                  <input
                    type="text"
                    required
                    className="w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-sm"
                    value={latitude}
                    onChange={(e) => setLatitude(e.target.value)}
                    placeholder="Latitude (e.g. 34.0522)"
                  />
                </div>
                <div className="flex-1">
                  <input
                    type="text"
                    required
                    className="w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-sm"
                    value={longitude}
                    onChange={(e) => setLongitude(e.target.value)}
                    placeholder="Longitude (e.g. -118.2437)"
                  />
                </div>
                <button
                  type="button"
                  onClick={handleGetLocation}
                  className="bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-300 px-4 py-3 rounded-xl font-medium transition-colors flex items-center gap-2 whitespace-nowrap"
                >
                  <MapPin size={18} />
                  Get Current
                </button>
              </div>
            </div>

            <div className="pt-2">
              <label className="block text-sm font-semibold text-slate-700 mb-2">Upload Image (Optional)</label>
              <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center hover:bg-slate-50 transition-colors">
                <input
                  type="file"
                  id="imageUpload"
                  accept="image/*"
                  className="hidden"
                  onChange={handleImageChange}
                />
                <label htmlFor="imageUpload" className="cursor-pointer flex flex-col items-center">
                  <div className="bg-blue-100 text-blue-600 p-3 rounded-full mb-3">
                    <Upload size={24} />
                  </div>
                  <span className="text-sm font-medium text-slate-700">
                    {image ? image.name : 'Click to select a photo'}
                  </span>
                  <span className="text-xs text-slate-500 mt-1">PNG, JPG up to 5MB</span>
                </label>
              </div>
            </div>

            <div className="pt-6 border-t border-slate-100">
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3.5 rounded-xl transition-colors shadow-md disabled:opacity-70 flex justify-center text-lg"
              >
                {loading ? 'Submitting Issue...' : 'Submit Issue'}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};

export default CreateIssue;
