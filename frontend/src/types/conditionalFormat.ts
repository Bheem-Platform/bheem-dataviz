/**
 * Conditional Formatting Types
 *
 * TypeScript types for conditional formatting rules.
 */

// Enums

export type FormatType =
  | 'color_scale'
  | 'data_bar'
  | 'icon_set'
  | 'rules'
  | 'top_bottom'
  | 'above_below_avg'
  | 'duplicate_unique';

export type ComparisonOperator =
  | 'equals'
  | 'not_equals'
  | 'greater_than'
  | 'greater_than_or_equal'
  | 'less_than'
  | 'less_than_or_equal'
  | 'between'
  | 'not_between'
  | 'contains'
  | 'not_contains'
  | 'starts_with'
  | 'ends_with'
  | 'is_blank'
  | 'is_not_blank';

export type FormatTarget = 'cell' | 'text' | 'background' | 'border';

// Color Types

export interface Color {
  hex?: string;
  rgb?: [number, number, number];
  rgba?: [number, number, number, number];
  name?: string;
}

export interface ColorStop {
  position: number;
  color: Color;
}

// Style Types

export interface TextStyle {
  color?: Color;
  fontWeight?: 'normal' | 'bold';
  fontStyle?: 'normal' | 'italic';
  textDecoration?: 'none' | 'underline' | 'line-through';
  fontSize?: string;
}

export interface BackgroundStyle {
  color?: Color;
  gradient?: ColorStop[];
  opacity?: number;
}

export interface BorderStyle {
  color?: Color;
  width?: string;
  style?: 'solid' | 'dashed' | 'dotted';
  sides?: ('all' | 'top' | 'right' | 'bottom' | 'left')[];
}

export interface FormatStyle {
  text?: TextStyle;
  background?: BackgroundStyle;
  border?: BorderStyle;
}

// Format Configurations

export interface ColorScaleConfig {
  minColor: Color;
  midColor?: Color;
  maxColor: Color;
  minType: 'min' | 'number' | 'percent' | 'percentile';
  minValue?: number;
  midType?: 'number' | 'percent' | 'percentile';
  midValue?: number;
  maxType: 'max' | 'number' | 'percent' | 'percentile';
  maxValue?: number;
}

export interface DataBarConfig {
  fillColor: Color;
  borderColor?: Color;
  negativeFillColor?: Color;
  negativeBorderColor?: Color;
  barDirection: 'context' | 'left_to_right' | 'right_to_left';
  showValue: boolean;
  minLength: number;
  maxLength: number;
  axisPosition: 'auto' | 'midpoint' | 'none';
  axisColor?: Color;
}

export interface IconSetConfig {
  iconSet: string;
  reverseOrder: boolean;
  showIconOnly: boolean;
  thresholds: {
    type: 'percent' | 'number' | 'percentile';
    value: number;
    iconIndex?: number;
  }[];
}

export interface FormatRule {
  id: string;
  name?: string;
  priority: number;
  enabled: boolean;
  stopIfTrue: boolean;
  operator: ComparisonOperator;
  value?: any;
  value2?: any;
  formula?: string;
  style: FormatStyle;
}

export interface RulesConfig {
  rules: FormatRule[];
  applyFirstMatchOnly: boolean;
}

export interface TopBottomConfig {
  type: 'top' | 'bottom';
  count: number;
  isPercent: boolean;
  style: FormatStyle;
}

export interface AboveBelowAvgConfig {
  type: 'above' | 'below' | 'above_or_equal' | 'below_or_equal';
  stdDev?: number;
  aboveStyle: FormatStyle;
  belowStyle?: FormatStyle;
}

// Main Conditional Format

export interface ConditionalFormat {
  id: string;
  name?: string;
  column: string;
  type: FormatType;
  enabled: boolean;
  priority: number;
  target: FormatTarget;
  colorScale?: ColorScaleConfig;
  dataBar?: DataBarConfig;
  iconSet?: IconSetConfig;
  rules?: RulesConfig;
  topBottom?: TopBottomConfig;
  aboveBelowAvg?: AboveBelowAvgConfig;
}

export interface ChartConditionalFormats {
  chartId: string;
  formats: ConditionalFormat[];
}

// Format Result (returned by evaluation)

export interface FormatResult {
  type: FormatType;
  backgroundColor?: string;
  width?: number;
  isNegative?: boolean;
  fillColor?: string;
  showValue?: boolean;
  direction?: string;
  icon?: string;
  ruleId?: string;
  style?: FormatStyle;
  position?: 'above' | 'below';
}

export interface FormattedRow {
  [key: string]: any;
  _formats?: Record<string, FormatResult[]>;
}

// Templates

export interface FormatTemplate {
  id: string;
  name: string;
  description: string;
  type: FormatType;
  config: Record<string, any>;
}

// Icon Sets

export const ICON_SETS: Record<string, string[]> = {
  traffic_light: ['green_circle', 'yellow_circle', 'red_circle'],
  traffic_light_rim: ['green_circle_rim', 'yellow_circle_rim', 'red_circle_rim'],
  arrows_3: ['arrow_up', 'arrow_right', 'arrow_down'],
  arrows_4: ['arrow_up', 'arrow_up_right', 'arrow_down_right', 'arrow_down'],
  arrows_5: ['arrow_up', 'arrow_up_right', 'arrow_right', 'arrow_down_right', 'arrow_down'],
  triangles: ['triangle_up', 'dash', 'triangle_down'],
  stars: ['star_full', 'star_half', 'star_empty'],
  ratings: ['rating_5', 'rating_4', 'rating_3', 'rating_2', 'rating_1'],
  flags: ['flag_green', 'flag_yellow', 'flag_red'],
  checkmarks: ['check', 'exclamation', 'x'],
};

// Preset Colors

export const PRESET_COLORS: Color[] = [
  { hex: '#FF0000', name: 'Red' },
  { hex: '#FF6600', name: 'Orange' },
  { hex: '#FFCC00', name: 'Yellow' },
  { hex: '#00FF00', name: 'Green' },
  { hex: '#0066FF', name: 'Blue' },
  { hex: '#6600FF', name: 'Purple' },
  { hex: '#FF00FF', name: 'Magenta' },
  { hex: '#FFFFFF', name: 'White' },
  { hex: '#000000', name: 'Black' },
  { hex: '#808080', name: 'Gray' },
];

// Gradient Presets

export const GRADIENT_PRESETS: { name: string; colors: [Color, Color] | [Color, Color, Color] }[] = [
  {
    name: 'Red-Yellow-Green',
    colors: [
      { hex: '#F8696B' },
      { hex: '#FFEB84' },
      { hex: '#63BE7B' },
    ],
  },
  {
    name: 'Green-Yellow-Red',
    colors: [
      { hex: '#63BE7B' },
      { hex: '#FFEB84' },
      { hex: '#F8696B' },
    ],
  },
  {
    name: 'Blue-White-Red',
    colors: [
      { hex: '#5A8AC6' },
      { hex: '#FFFFFF' },
      { hex: '#F8696B' },
    ],
  },
  {
    name: 'White-Blue',
    colors: [
      { hex: '#FFFFFF' },
      { hex: '#5A8AC6' },
    ],
  },
  {
    name: 'White-Red',
    colors: [
      { hex: '#FFFFFF' },
      { hex: '#F8696B' },
    ],
  },
];

// Helper Functions

export function colorToHex(color: Color): string {
  if (color.hex) return color.hex;
  if (color.rgb) {
    const [r, g, b] = color.rgb;
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  }
  if (color.rgba) {
    const [r, g, b] = color.rgba;
    return `#${Math.round(r).toString(16).padStart(2, '0')}${Math.round(g).toString(16).padStart(2, '0')}${Math.round(b).toString(16).padStart(2, '0')}`;
  }
  return '#000000';
}

export function createDefaultFormat(column: string, type: FormatType): ConditionalFormat {
  const baseFormat: ConditionalFormat = {
    id: `${type}_${Date.now()}`,
    column,
    type,
    enabled: true,
    priority: 0,
    target: 'cell',
  };

  switch (type) {
    case 'color_scale':
      baseFormat.colorScale = {
        minColor: { hex: '#F8696B' },
        midColor: { hex: '#FFEB84' },
        maxColor: { hex: '#63BE7B' },
        minType: 'min',
        maxType: 'max',
      };
      break;

    case 'data_bar':
      baseFormat.dataBar = {
        fillColor: { hex: '#638EC6' },
        barDirection: 'context',
        showValue: true,
        minLength: 0,
        maxLength: 100,
        axisPosition: 'auto',
      };
      break;

    case 'icon_set':
      baseFormat.iconSet = {
        iconSet: 'traffic_light',
        reverseOrder: false,
        showIconOnly: false,
        thresholds: [
          { type: 'percent', value: 67, iconIndex: 0 },
          { type: 'percent', value: 33, iconIndex: 1 },
        ],
      };
      break;

    case 'rules':
      baseFormat.rules = {
        rules: [],
        applyFirstMatchOnly: true,
      };
      break;

    case 'top_bottom':
      baseFormat.topBottom = {
        type: 'top',
        count: 10,
        isPercent: false,
        style: {
          background: { color: { hex: '#FFEB84' } },
        },
      };
      break;

    case 'above_below_avg':
      baseFormat.aboveBelowAvg = {
        type: 'above',
        aboveStyle: {
          background: { color: { hex: '#63BE7B' } },
        },
        belowStyle: {
          background: { color: { hex: '#F8696B' } },
        },
      };
      break;
  }

  return baseFormat;
}
