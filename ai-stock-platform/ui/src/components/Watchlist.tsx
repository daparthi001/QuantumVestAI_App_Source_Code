/**
 * Watchlist Component
 * Manage and view user watchlists with full API integration
 */
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiService, { Watchlist } from '../services/api-service';

const WatchlistComponent: React.FC = () => {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [showAddStockModal, setShowAddStockModal] = useState<boolean>(false);
  const [selectedWatchlist, setSelectedWatchlist] = useState<Watchlist | null>(null);
  const [newWatchlistName, setNewWatchlistName] = useState<string>('');
  const [newStockSymbol, setNewStockSymbol] = useState<string>('');
  const [creating, setCreating] = useState<boolean>(false);
  const [adding, setAdding] = useState<boolean>(false);

  useEffect(() => {
    fetchWatchlists();
  }, []);

  const fetchWatchlists = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getWatchlists();
      setWatchlists(data);
    } catch (err) {
      console.error('Error fetching watchlists:', err);
      setError('Failed to load watchlists. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWatchlist = async () => {
    if (!newWatchlistName.trim()) return;

    try {
      setCreating(true);
      await apiService.createWatchlist({ name: newWatchlistName.trim() });
      setNewWatchlistName('');
      setShowCreateModal(false);
      await fetchWatchlists();
    } catch (err) {
      console.error('Error creating watchlist:', err);
      setError('Failed to create watchlist. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  const handleAddStock = async () => {
    if (!newStockSymbol.trim() || !selectedWatchlist) return;

    try {
      setAdding(true);
      await apiService.addToWatchlist(selectedWatchlist.id, newStockSymbol.trim().toUpperCase());
      setNewStockSymbol('');
      setShowAddStockModal(false);
      setSelectedWatchlist(null);
      await fetchWatchlists();
    } catch (err) {
      console.error('Error adding stock:', err);
      setError('Failed to add stock to watchlist. Please try again.');
    } finally {
      setAdding(false);
    }
  };

  const handleRemoveStock = async (watchlistId: number, symbol: string) => {
    if (!window.confirm(`Remove ${symbol} from watchlist?`)) return;

    try {
      await apiService.removeFromWatchlist(watchlistId, symbol);
      await fetchWatchlists();
    } catch (err) {
      console.error('Error removing stock:', err);
      setError('Failed to remove stock from watchlist. Please try again.');
    }
  };

  const handleDeleteWatchlist = async (watchlistId: number) => {
    if (!window.confirm('Are you sure you want to delete this watchlist?')) return;

    try {
      await apiService.deleteWatchlist(watchlistId);
      await fetchWatchlists();
    } catch (err) {
      console.error('Error deleting watchlist:', err);
      setError('Failed to delete watchlist. Please try again.');
    }
  };

  const formatPrice = (price: number) => {
    return price.toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    });
  };

  return (
    <div className="max-w-5xl mx-auto p-4">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold">My Watchlists</h1>
        <button
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg"
          onClick={() => setShowCreateModal(true)}
        >
          Create New Watchlist
        </button>
      </div>

      {error && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-4 flex justify-between">
          <span>{error}</span>
          <button className="underline" onClick={fetchWatchlists}>Retry</button>
        </div>
      )}

      {loading ? (
        <div className="text-center py-10">
          <div className="w-8 h-8 mx-auto border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <p className="mt-2 text-gray-500">Loading watchlists...</p>
        </div>
      ) : watchlists.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow text-center">
          <h5 className="text-lg font-semibold mb-2">No Watchlists Yet</h5>
          <p className="text-gray-500 mb-4">Create your first watchlist to start tracking your favorite stocks.</p>
          <button
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg"
            onClick={() => setShowCreateModal(true)}
          >
            Create Your First Watchlist
          </button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {watchlists.map((watchlist) => (
            <div key={watchlist.id} className="bg-white dark:bg-gray-800 rounded-xl shadow">
              <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
                <div>
                  <h5 className="font-semibold">{watchlist.name}</h5>
                  <small className="text-gray-500">
                    {watchlist.stocks.length} stock{watchlist.stocks.length !== 1 ? 's' : ''}
                  </small>
                </div>
                <div className="space-x-2">
                  <button
                    className="px-2 py-1 text-sm bg-blue-600 hover:bg-blue-500 text-white rounded"
                    onClick={() => {
                      setSelectedWatchlist(watchlist);
                      setShowAddStockModal(true);
                    }}
                  >
                    Add Stock
                  </button>
                  <button
                    className="px-2 py-1 text-sm bg-red-600 hover:bg-red-500 text-white rounded"
                    onClick={() => handleDeleteWatchlist(watchlist.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
              <div className="p-4">
                {watchlist.stocks.length === 0 ? (
                  <div className="text-center text-gray-500">
                    <p>No stocks in this watchlist yet.</p>
                    <button
                      className="mt-2 px-3 py-1 text-sm border border-blue-600 text-blue-600 rounded hover:bg-blue-600 hover:text-white"
                      onClick={() => {
                        setSelectedWatchlist(watchlist);
                        setShowAddStockModal(true);
                      }}
                    >
                      Add Your First Stock
                    </button>
                  </div>
                ) : (
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="py-1 text-left">Symbol</th>
                        <th className="py-1 text-left">Name</th>
                        <th className="py-1 text-left">Price</th>
                        <th className="py-1 text-left">Change %</th>
                        <th className="py-1 text-left">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {watchlist.stocks.map((stock) => (
                        <tr key={stock.symbol} className="border-b last:border-none">
                          <td className="py-1">
                            <Link to={`/stocks/${stock.symbol}`} className="font-semibold hover:underline">
                              {stock.symbol}
                            </Link>
                          </td>
                          <td className="py-1">{stock.name}</td>
                          <td className="py-1">{formatPrice(stock.price)}</td>
                          <td className="py-1">
                            <span className={stock.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}>
                              {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                            </span>
                          </td>
                          <td className="py-1">
                            <button
                              className="text-red-600 hover:underline"
                              onClick={() => handleRemoveStock(watchlist.id, stock.symbol)}
                            >
                              Remove
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg w-80 space-y-4">
            <h3 className="text-lg font-semibold">Create New Watchlist</h3>
            <input
              type="text"
              value={newWatchlistName}
              onChange={(e) => setNewWatchlistName(e.target.value)}
              placeholder="Watchlist Name"
              className="w-full px-3 py-2 border rounded focus:outline-none focus:ring"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-3 py-2 rounded bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateWatchlist}
                disabled={!newWatchlistName.trim() || creating}
                className="px-3 py-2 rounded bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50"
              >
                {creating ? 'Creating...' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}

      {showAddStockModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg w-80 space-y-4">
            <h3 className="text-lg font-semibold">Add Stock to {selectedWatchlist?.name}</h3>
            <input
              type="text"
              value={newStockSymbol}
              onChange={(e) => setNewStockSymbol(e.target.value)}
              placeholder="Stock Symbol (e.g., AAPL)"
              style={{ textTransform: 'uppercase' }}
              className="w-full px-3 py-2 border rounded focus:outline-none focus:ring"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowAddStockModal(false)}
                className="px-3 py-2 rounded bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={handleAddStock}
                disabled={!newStockSymbol.trim() || adding}
                className="px-3 py-2 rounded bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50"
              >
                {adding ? 'Adding...' : 'Add Stock'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WatchlistComponent;
