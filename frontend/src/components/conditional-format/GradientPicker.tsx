/**
 * Gradient Picker Component
 *
 * A gradient color picker for color scale conditional formatting.
 */

import React, { useState } from 'react';
import { Palette, Plus, Minus } from 'lucide-react';
import {
  Color,
  ColorScaleConfig,
  GRADIENT_PRESETS,
  colorToHex,
} from '../../types/conditionalFormat';
import { ColorPicker } from './ColorPicker';
import { cn } from '../../lib/utils';

interface GradientPickerProps {
  value: ColorScaleConfig;
  onChange: (config: ColorScaleConfig) => void;
  showMidpoint?: boolean;
  className?: string;
}

export const GradientPicker: React.FC<GradientPickerProps> = ({
  value,
  onChange,
  showMidpoint = true,
  className,
}) => {
  const [useMidpoint, setUseMidpoint] = useState(!!value.midColor);

  // Generate gradient CSS
  const gradientCss = useMidpoint && value.midColor
    ? `linear-gradient(to right, ${colorToHex(value.minColor)}, ${colorToHex(value.midColor)}, ${colorToHex(value.maxColor)})`
    : `linear-gradient(to right, ${colorToHex(value.minColor)}, ${colorToHex(value.maxColor)})`;

  const handleMinColorChange = (color: Color) => {
    onChange({ ...value, minColor: color });
  };

  const handleMidColorChange = (color: Color) => {
    onChange({ ...value, midColor: color });
  };

  const handleMaxColorChange = (color: Color) => {
    onChange({ ...value, maxColor: color });
  };

  const handleToggleMidpoint = () => {
    if (useMidpoint) {
      // Remove midpoint
      setUseMidpoint(false);
      onChange({
        ...value,
        midColor: undefined,
        midType: undefined,
        midValue: undefined,
      });
    } else {
      // Add midpoint
      setUseMidpoint(true);
      onChange({
        ...value,
        midColor: { hex: '#FFEB84' },
        midType: 'percent',
        midValue: 50,
      });
    }
  };

  const handlePresetSelect = (preset: typeof GRADIENT_PRESETS[0]) => {
    if (preset.colors.length === 3) {
      setUseMidpoint(true);
      onChange({
        ...value,
        minColor: preset.colors[0],
        midColor: preset.colors[1],
        maxColor: preset.colors[2],
        midType: 'percent',
        midValue: 50,
      });
    } else {
      setUseMidpoint(false);
      onChange({
        ...value,
        minColor: preset.colors[0],
        maxColor: preset.colors[1],
        midColor: undefined,
        midType: undefined,
        midValue: undefined,
      });
    }
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Gradient Preview */}
      <div
        className="h-8 rounded-md border border-gray-300"
        style={{ background: gradientCss }}
      />

      {/* Preset Gradients */}
      <div>
        <label className="block text-xs font-medium text-gray-500 mb-2">
          Presets
        </label>
        <div className="flex flex-wrap gap-2">
          {GRADIENT_PRESETS.map((preset) => {
            const presetGradient =
              preset.colors.length === 3
                ? `linear-gradient(to right, ${colorToHex(preset.colors[0])}, ${colorToHex(preset.colors[1])}, ${colorToHex(preset.colors[2])})`
                : `linear-gradient(to right, ${colorToHex(preset.colors[0])}, ${colorToHex(preset.colors[1])})`;

            return (
              <button
                key={preset.name}
                type="button"
                onClick={() => handlePresetSelect(preset)}
                className="flex items-center gap-2 px-2 py-1 border border-gray-200 rounded-md hover:border-gray-400"
                title={preset.name}
              >
                <div
                  className="w-12 h-4 rounded"
                  style={{ background: presetGradient }}
                />
              </button>
            );
          })}
        </div>
      </div>

      {/* Color Pickers */}
      <div className="grid grid-cols-3 gap-4">
        {/* Min Color */}
        <div>
          <ColorPicker
            value={value.minColor}
            onChange={handleMinColorChange}
            label="Min"
          />
          <select
            value={value.minType}
            onChange={(e) => onChange({ ...value, minType: e.target.value as any })}
            className="mt-1 w-full px-2 py-1 text-xs border border-gray-300 rounded-md"
          >
            <option value="min">Minimum</option>
            <option value="number">Number</option>
            <option value="percent">Percent</option>
            <option value="percentile">Percentile</option>
          </select>
          {value.minType !== 'min' && (
            <input
              type="number"
              value={value.minValue || 0}
              onChange={(e) => onChange({ ...value, minValue: Number(e.target.value) })}
              className="mt-1 w-full px-2 py-1 text-xs border border-gray-300 rounded-md"
              placeholder="Value"
            />
          )}
        </div>

        {/* Mid Color (optional) */}
        {showMidpoint && (
          <div>
            {useMidpoint && value.midColor ? (
              <>
                <ColorPicker
                  value={value.midColor}
                  onChange={handleMidColorChange}
                  label="Mid"
                />
                <select
                  value={value.midType || 'percent'}
                  onChange={(e) => onChange({ ...value, midType: e.target.value as any })}
                  className="mt-1 w-full px-2 py-1 text-xs border border-gray-300 rounded-md"
                >
                  <option value="number">Number</option>
                  <option value="percent">Percent</option>
                  <option value="percentile">Percentile</option>
                </select>
                <input
                  type="number"
                  value={value.midValue || 50}
                  onChange={(e) => onChange({ ...value, midValue: Number(e.target.value) })}
                  className="mt-1 w-full px-2 py-1 text-xs border border-gray-300 rounded-md"
                  placeholder="Value"
                />
              </>
            ) : (
              <button
                type="button"
                onClick={handleToggleMidpoint}
                className="w-full h-full flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-md text-gray-500 hover:border-gray-400 hover:text-gray-600"
              >
                <Plus className="h-5 w-5" />
                <span className="text-xs mt-1">Add Midpoint</span>
              </button>
            )}
          </div>
        )}

        {/* Max Color */}
        <div>
          <ColorPicker
            value={value.maxColor}
            onChange={handleMaxColorChange}
            label="Max"
          />
          <select
            value={value.maxType}
            onChange={(e) => onChange({ ...value, maxType: e.target.value as any })}
            className="mt-1 w-full px-2 py-1 text-xs border border-gray-300 rounded-md"
          >
            <option value="max">Maximum</option>
            <option value="number">Number</option>
            <option value="percent">Percent</option>
            <option value="percentile">Percentile</option>
          </select>
          {value.maxType !== 'max' && (
            <input
              type="number"
              value={value.maxValue || 0}
              onChange={(e) => onChange({ ...value, maxValue: Number(e.target.value) })}
              className="mt-1 w-full px-2 py-1 text-xs border border-gray-300 rounded-md"
              placeholder="Value"
            />
          )}
        </div>
      </div>

      {/* Toggle Midpoint Button */}
      {showMidpoint && useMidpoint && (
        <button
          type="button"
          onClick={handleToggleMidpoint}
          className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700"
        >
          <Minus className="h-3 w-3" />
          Remove Midpoint
        </button>
      )}
    </div>
  );
};

export default GradientPicker;
