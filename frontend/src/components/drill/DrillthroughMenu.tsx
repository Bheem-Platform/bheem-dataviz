/**
 * Drillthrough Menu Component
 *
 * Context menu for drillthrough options when right-clicking chart elements.
 */

import React, { useState, useEffect, useRef } from 'react';
import { ExternalLink, FileText, Layout, Link2 } from 'lucide-react';
import { DrillthroughTarget, DrillthroughConfig } from '../../types/drill';
import { cn } from '../../lib/utils';

interface DrillthroughMenuProps {
  config: DrillthroughConfig;
  clickedData: Record<string, any>;
  position: { x: number; y: number };
  onSelect: (target: DrillthroughTarget) => void;
  onClose: () => void;
  className?: string;
}

export const DrillthroughMenu: React.FC<DrillthroughMenuProps> = ({
  config,
  clickedData,
  position,
  onSelect,
  onClose,
  className,
}) => {
  const menuRef = useRef<HTMLDivElement>(null);
  const [adjustedPosition, setAdjustedPosition] = useState(position);

  // Adjust position to keep menu in viewport
  useEffect(() => {
    if (menuRef.current) {
      const rect = menuRef.current.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      let x = position.x;
      let y = position.y;

      // Adjust horizontal position
      if (x + rect.width > viewportWidth - 10) {
        x = viewportWidth - rect.width - 10;
      }

      // Adjust vertical position
      if (y + rect.height > viewportHeight - 10) {
        y = viewportHeight - rect.height - 10;
      }

      setAdjustedPosition({ x, y });
    }
  }, [position]);

  // Close on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [onClose]);

  if (!config.enabled || config.targets.length === 0) {
    return null;
  }

  const getIcon = (target: DrillthroughTarget) => {
    if (target.icon) {
      // Custom icon support could be added here
      return <FileText className="h-4 w-4" />;
    }

    switch (target.targetType) {
      case 'page':
        return <Layout className="h-4 w-4" />;
      case 'report':
        return <FileText className="h-4 w-4" />;
      case 'url':
        return <ExternalLink className="h-4 w-4" />;
      default:
        return <Link2 className="h-4 w-4" />;
    }
  };

  // Format clicked data for display
  const clickedDataDisplay = Object.entries(clickedData)
    .filter(([_, value]) => value != null)
    .slice(0, 3)
    .map(([key, value]) => `${key}: ${value}`)
    .join(', ');

  return (
    <div
      ref={menuRef}
      className={cn(
        'fixed z-50 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden',
        'min-w-[200px] max-w-[300px]',
        className
      )}
      style={{
        left: adjustedPosition.x,
        top: adjustedPosition.y,
      }}
    >
      {/* Header */}
      <div className="px-3 py-2 bg-gray-50 border-b">
        <div className="text-xs font-medium text-gray-500 uppercase">
          Drillthrough
        </div>
        {clickedDataDisplay && (
          <div className="text-xs text-gray-600 truncate mt-0.5">
            {clickedDataDisplay}
          </div>
        )}
      </div>

      {/* Targets */}
      <div className="py-1">
        {config.targets.map((target) => (
          <button
            key={target.id}
            onClick={() => onSelect(target)}
            className="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 text-left"
          >
            <span className="text-gray-500">
              {getIcon(target)}
            </span>
            <div className="flex-1 min-w-0">
              <div className="font-medium truncate">{target.name}</div>
              {target.targetType === 'url' && (
                <div className="text-xs text-gray-500 truncate">
                  {target.targetUrl}
                </div>
              )}
            </div>
            {target.openInNewTab && (
              <ExternalLink className="h-3 w-3 text-gray-400" />
            )}
          </button>
        ))}
      </div>

      {/* Default Target Hint */}
      {config.defaultTargetId && (
        <div className="px-3 py-1.5 bg-gray-50 border-t text-xs text-gray-500">
          Double-click for default action
        </div>
      )}
    </div>
  );
};

export default DrillthroughMenu;
