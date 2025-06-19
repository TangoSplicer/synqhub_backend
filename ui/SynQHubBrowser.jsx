// synq/ui/SynQHubBrowser.jsx

import React, { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Sparkles, CheckCircle, XCircle } from "lucide-react";

const MOCK_PLUGIN_REGISTRY = [
  {
    id: "plugin_001",
    name: "Quantum Fourier Transformer",
    author: "QDev",
    description: "Applies QFT and inverse QFT for spectral analysis.",
    tags: ["quantum", "fourier", "math"],
    version: "1.2.3",
    license: "MIT",
    score: 92,
    signed: true,
    published: "2025-06-17"
  },
  {
    id: "plugin_002",
    name: "AI Fusion Optimizer",
    author: "SynQAI",
    description: "Uses reranking and AI agents to optimize gate sequences.",
    tags: ["ai", "optimizer", "autotune"],
    version: "0.9.5",
    license: "Apache-2.0",
    score: 87,
    signed: false,
    published: "2025-06-12"
  }
];

function PluginCard({ plugin, onClick }) {
  return (
    <Card onClick={() => onClick(plugin)} className="cursor-pointer transition hover:shadow-xl rounded-2xl p-4 m-2">
      <CardContent>
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold">{plugin.name}</h2>
          <SignatureStatusBadge signed={plugin.signed} />
        </div>
        <p className="text-sm text-gray-500 mb-1">by {plugin.author}</p>
        <p className="text-sm">{plugin.description}</p>
        <div className="flex gap-1 mt-2 flex-wrap">
          {plugin.tags.map((tag, i) => (
            <Badge key={i} variant="outline">{tag}</Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function SignatureStatusBadge({ signed }) {
  return signed ? (
    <Badge className="bg-green-600 text-white">
      <CheckCircle size={14} className="mr-1" /> Signed
    </Badge>
  ) : (
    <Badge className="bg-red-600 text-white">
      <XCircle size={14} className="mr-1" /> Unsigned
    </Badge>
  );
}

function PluginDetailModal({ plugin, open, onClose }) {
  if (!plugin) return null;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{plugin.name}</DialogTitle>
        </DialogHeader>
        <div className="text-sm text-gray-500 mb-2">by {plugin.author}</div>
        <div className="text-sm">{plugin.description}</div>
        <div className="mt-2">
          <strong>Version:</strong> {plugin.version}  
          <span className="ml-4"><strong>Published:</strong> {plugin.published}</span>
        </div>
        <div className="mt-2">
          <strong>License:</strong> {plugin.license}
        </div>
        <div className="mt-2">
          <strong>Tags:</strong> {plugin.tags.join(", ")}
        </div>
        <div className="mt-2">
          <strong>AI Quality Score:</strong> {plugin.score} / 100
        </div>
        <div className="mt-4 flex gap-3">
          <Button variant="default">🔍 Preview</Button>
          <Button variant="secondary">⬇️ Install</Button>
          <Button variant="outline" className="ml-auto">
            {plugin.signed ? "🔐 Verify Signature" : "✍️ Sign Plugin"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default function SynQHubBrowser() {
  const [search, setSearch] = useState("");
  const [plugins, setPlugins] = useState(MOCK_PLUGIN_REGISTRY);
  const [selectedPlugin, setSelectedPlugin] = useState(null);

  const filteredPlugins = plugins.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.tags.join(" ").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6">
      <div className="flex items-center mb-6">
        <Sparkles className="text-purple-600 mr-2" />
        <h1 className="text-2xl font-bold">SynQHUB Plugin Browser</h1>
      </div>
      <Input
        className="mb-4"
        placeholder="Search plugins by name, tag, or feature..."
        value={search}
        onChange={e => setSearch(e.target.value)}
      />
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {filteredPlugins.map(plugin => (
          <PluginCard key={plugin.id} plugin={plugin} onClick={setSelectedPlugin} />
        ))}
      </div>
      <PluginDetailModal plugin={selectedPlugin} open={!!selectedPlugin} onClose={() => setSelectedPlugin(null)} />
    </div>
  );
}
