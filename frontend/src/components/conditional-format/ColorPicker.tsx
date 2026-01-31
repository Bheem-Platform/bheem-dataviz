/**
 * Color Picker Component
 *
 * A color picker for conditional formatting with preset colors and custom input.
 */

import React, { useState } from 'react';
import { Palette, Check } from 'lucide-react';
import { Color, PRESET_COLORS, colorToHex } from '../../types/conditionalFormat';
import { cn } from '../../lib/utils';

interface ColorPickerProps {
  value: Color;
  onChange: (color: Color) => void;
  label?: string;
  showInput?: boolean;
  presets?: Color[];
  className?: string;
}

export const ColorPicker: React.FC<ColorPickerProps> = ({
  value,
  onChange,
  label,
  showInput = true,
  presets = PRESET_COLORS,
  className,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [customHex, setCustomHex] = useState(colorToHex(value));

  const currentHex = colorToHex(value);

  const handlePresetClick = (preset: Color) => {
    onChange(preset);
    setCustomHex(colorToHex(preset));
    setIsOpen(false);
  };

  const handleCustomChange = (hex: string) => {
    setCustomHex(hex);
    if (/^#[0-9A-Fa-f]{6}$/.test(hex)) {
      onChange({ hex });
    }
  };

  return (
    <div className={cn('relative', className)}>
      {label && (
        <label className="block text-xs font-medium text-gray-500 mb-1">
          {label}
        </label>
      )}

      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-md bg-white hover:bg-gray-50"
      >
        <div
          className="w-5 h-5 rounded border border-gray-300"
          style={{ backgroundColor: currentHex }}
        />
        <span className="text-sm text-gray-700">{currentHex}</span>
        <Palette className="h-4 w-4 text-gray-400" />
      </button>

      {/* Dropdown */}
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute z-20 mt-1 p-3 bg-white border border-gray-200 rounded-lg shadow-lg w-56">
            {/* Preset Colors */}
            <div className="grid grid-cols-5 gap-1.5 mb-3">
              {presets.map((preset, idx) => {
                const presetHex = colorToHex(preset);
                const isSelected = presetHex.toLowerCase() === currentHex.toLowerCase();

                return (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handlePresetClick(preset)}
                    className={cn(
                      'w-8 h-8 rounded border-2 flex items-center justify-center transition-all',
                      isSelected
                        ? 'border-blue-500 scale-110'
                        : 'border-gray-200 hover:border-gray-400'
                    )}
                    style={{ backgroundColor: presetHex }}
                    title={preset.name || presetHex}
                  >
                    {isSelected && (
                      <Check
                        className={cn(
                          'h-4 w-4',
                          parseInt(presetHex.slice(1), 16) > 0x808080
                            ? 'text-gray-800'
                            : 'text-white'
                        )}
                      />
                    )}
                  </button>
                );
              })}
            </div>

            {/* Custom Hex Input */}
            {showInput && (
              <div className="pt-2 border-t">
                <label className="block text-xs font-medium text-gray-500 mb-1">
                  Custom Color
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={currentHex}
                    onChange={(e) => handleCustomChange(e.target.value)}
                    className="w-8 h-8 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={customHex}
                    onChange={(e) => handleCustomChange(e.target.value)}
                    placeholder="#000000"
                    className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default ColorPicker;
