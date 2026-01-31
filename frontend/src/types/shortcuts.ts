/**
 * Shortcuts & Command Palette Types
 *
 * TypeScript types for keyboard shortcuts and command palette features.
 */

// Enums

export enum CommandCategory {
  NAVIGATION = 'navigation',
  DASHBOARD = 'dashboard',
  CHART = 'chart',
  DATA = 'data',
  EDIT = 'edit',
  VIEW = 'view',
  HELP = 'help',
  SYSTEM = 'system',
  RECENT = 'recent',
  FAVORITE = 'favorite',
}

export enum ActionType {
  NAVIGATE = 'navigate',
  OPEN = 'open',
  CREATE = 'create',
  SEARCH = 'search',
  TOGGLE = 'toggle',
  EXECUTE = 'execute',
  MODAL = 'modal',
  EXTERNAL = 'external',
}

export enum ShortcutScope {
  GLOBAL = 'global',
  DASHBOARD = 'dashboard',
  CHART = 'chart',
  EDITOR = 'editor',
  TABLE = 'table',
  MODAL = 'modal',
}

// Shortcut Types

export interface KeyBinding {
  key: string;
  modifiers: string[];
  display?: string | null;
}

export interface ShortcutAction {
  action_type: ActionType;
  target?: string | null;
  params: Record<string, unknown>;
}

export interface Shortcut {
  id: string;
  name: string;
  description?: string | null;
  category: CommandCategory;
  key_binding: KeyBinding;
  action: ShortcutAction;
  scope: ShortcutScope;
  enabled: boolean;
  is_default: boolean;
  is_customizable: boolean;
}

export interface ShortcutOverride {
  shortcut_id: string;
  key_binding?: KeyBinding | null;
  enabled?: boolean | null;
}

// Command Types

export interface CommandIcon {
  type: 'lucide' | 'emoji' | 'url';
  value: string;
}

export interface Command {
  id: string;
  title: string;
  subtitle?: string | null;
  description?: string | null;
  icon?: CommandIcon | null;
  category: CommandCategory;
  keywords: string[];
  action: ShortcutAction;
  shortcut?: KeyBinding | null;
  score: number;
  is_recent: boolean;
  is_favorite: boolean;
  last_used?: string | null;
  use_count: number;
}

export interface CommandGroup {
  id: string;
  name: string;
  commands: Command[];
  priority: number;
}

export interface CommandPaletteState {
  isOpen: boolean;
  query: string;
  selectedIndex: number;
  mode: 'search' | 'recent' | 'actions';
  filterCategory?: CommandCategory | null;
}

// Preferences Types

export interface ShortcutPreferences {
  user_id: string;
  overrides: ShortcutOverride[];
  disabled_shortcuts: string[];
  custom_shortcuts: Shortcut[];
  show_hints: boolean;
  enable_vim_mode: boolean;
  hold_time_ms: number;
  updated_at?: string | null;
}

export interface RecentCommand {
  command_id: string;
  used_at: string;
  context?: Record<string, unknown> | null;
}

export interface CommandHistory {
  user_id: string;
  recent_commands: RecentCommand[];
  favorite_commands: string[];
  command_counts: Record<string, number>;
}

// Search Types

export interface CommandSearchResult {
  command: Command;
  match_type: 'title' | 'keyword' | 'description';
  match_positions: number[];
  score: number;
}

export interface CommandSearchResponse {
  results: CommandSearchResult[];
  total: number;
  query: string;
  suggestions: string[];
}

// Category Info

export interface CategoryInfo {
  id: string;
  name: string;
  count: number;
}

// Constants

export const MODIFIER_SYMBOLS: Record<string, string> = {
  cmd: '⌘',
  ctrl: '⌃',
  alt: '⌥',
  shift: '⇧',
  meta: '⌘',
};

export const CATEGORY_LABELS: Record<CommandCategory, string> = {
  [CommandCategory.NAVIGATION]: 'Navigation',
  [CommandCategory.DASHBOARD]: 'Dashboard',
  [CommandCategory.CHART]: 'Chart',
  [CommandCategory.DATA]: 'Data',
  [CommandCategory.EDIT]: 'Edit',
  [CommandCategory.VIEW]: 'View',
  [CommandCategory.HELP]: 'Help',
  [CommandCategory.SYSTEM]: 'System',
  [CommandCategory.RECENT]: 'Recent',
  [CommandCategory.FAVORITE]: 'Favorites',
};

export const CATEGORY_ICONS: Record<CommandCategory, string> = {
  [CommandCategory.NAVIGATION]: 'compass',
  [CommandCategory.DASHBOARD]: 'layout-dashboard',
  [CommandCategory.CHART]: 'bar-chart',
  [CommandCategory.DATA]: 'database',
  [CommandCategory.EDIT]: 'edit',
  [CommandCategory.VIEW]: 'eye',
  [CommandCategory.HELP]: 'help-circle',
  [CommandCategory.SYSTEM]: 'settings',
  [CommandCategory.RECENT]: 'clock',
  [CommandCategory.FAVORITE]: 'star',
};

// Helper Functions

export function getModifierSymbol(modifier: string): string {
  return MODIFIER_SYMBOLS[modifier.toLowerCase()] || modifier;
}

export function formatKeyBinding(binding: KeyBinding): string {
  if (binding.display) return binding.display;

  const parts = binding.modifiers.map(getModifierSymbol);
  parts.push(binding.key.length === 1 ? binding.key.toUpperCase() : binding.key);
  return parts.join('');
}

export function parseKeyBinding(display: string): KeyBinding {
  const modifiers: string[] = [];
  let key = display;

  // Extract modifiers
  Object.entries(MODIFIER_SYMBOLS).forEach(([mod, symbol]) => {
    if (display.includes(symbol)) {
      modifiers.push(mod);
      key = key.replace(symbol, '');
    }
  });

  return { key, modifiers, display };
}

export function matchKeyEvent(
  binding: KeyBinding,
  event: KeyboardEvent
): boolean {
  const key = event.key.toLowerCase();
  const bindingKey = binding.key.toLowerCase();

  if (key !== bindingKey) return false;

  const eventMods = new Set<string>();
  if (event.metaKey) eventMods.add('cmd');
  if (event.ctrlKey) eventMods.add('ctrl');
  if (event.altKey) eventMods.add('alt');
  if (event.shiftKey) eventMods.add('shift');

  const bindingMods = new Set(binding.modifiers.map((m) => m.toLowerCase()));

  if (eventMods.size !== bindingMods.size) return false;

  for (const mod of eventMods) {
    if (!bindingMods.has(mod)) return false;
  }

  return true;
}

export function highlightMatches(text: string, positions: number[]): string {
  if (!positions.length) return text;

  const chars = text.split('');
  const posSet = new Set(positions);

  return chars
    .map((char, i) => (posSet.has(i) ? `<mark>${char}</mark>` : char))
    .join('');
}

export function fuzzyMatch(
  query: string,
  text: string
): { matched: boolean; score: number; positions: number[] } {
  const q = query.toLowerCase();
  const t = text.toLowerCase();

  if (!q) return { matched: true, score: 1, positions: [] };

  const positions: number[] = [];
  let queryIdx = 0;
  let consecutive = 0;
  let score = 0;

  for (let textIdx = 0; textIdx < t.length && queryIdx < q.length; textIdx++) {
    if (t[textIdx] === q[queryIdx]) {
      positions.push(textIdx);

      if (positions.length > 1 && textIdx === positions[positions.length - 2] + 1) {
        consecutive++;
        score += consecutive * 2;
      } else {
        consecutive = 0;
        score += 1;
      }

      if (textIdx === 0 || ' -_'.includes(t[textIdx - 1])) {
        score += 5;
      }

      queryIdx++;
    }
  }

  const matched = queryIdx === q.length;
  const finalScore = matched ? score / t.length : 0;

  return { matched, score: finalScore, positions };
}

export function createKeyBindingFromEvent(event: KeyboardEvent): KeyBinding {
  const modifiers: string[] = [];
  if (event.metaKey) modifiers.push('cmd');
  if (event.ctrlKey) modifiers.push('ctrl');
  if (event.altKey) modifiers.push('alt');
  if (event.shiftKey) modifiers.push('shift');

  return {
    key: event.key,
    modifiers,
  };
}

// Default command palette initial state
export function createInitialPaletteState(): CommandPaletteState {
  return {
    isOpen: false,
    query: '',
    selectedIndex: 0,
    mode: 'search',
    filterCategory: null,
  };
}

// Shortcut manager class for client-side handling
export class ShortcutManager {
  private shortcuts: Map<string, Shortcut> = new Map();
  private handlers: Map<string, () => void> = new Map();
  private enabled = true;

  constructor(shortcuts: Shortcut[] = []) {
    shortcuts.forEach((s) => this.register(s));
  }

  register(shortcut: Shortcut): void {
    this.shortcuts.set(shortcut.id, shortcut);
  }

  unregister(shortcutId: string): void {
    this.shortcuts.delete(shortcutId);
    this.handlers.delete(shortcutId);
  }

  onShortcut(shortcutId: string, handler: () => void): () => void {
    this.handlers.set(shortcutId, handler);
    return () => this.handlers.delete(shortcutId);
  }

  enable(): void {
    this.enabled = true;
  }

  disable(): void {
    this.enabled = false;
  }

  handleKeyDown = (event: KeyboardEvent): boolean => {
    if (!this.enabled) return false;

    // Ignore when typing in inputs
    const target = event.target as HTMLElement;
    if (
      target.tagName === 'INPUT' ||
      target.tagName === 'TEXTAREA' ||
      target.isContentEditable
    ) {
      // Allow some shortcuts in inputs
      const allowedInInputs = ['Escape', 'Tab'];
      if (!allowedInInputs.includes(event.key)) return false;
    }

    for (const [id, shortcut] of this.shortcuts) {
      if (!shortcut.enabled) continue;

      if (matchKeyEvent(shortcut.key_binding, event)) {
        const handler = this.handlers.get(id);
        if (handler) {
          event.preventDefault();
          event.stopPropagation();
          handler();
          return true;
        }
      }
    }

    return false;
  };

  getAll(): Shortcut[] {
    return Array.from(this.shortcuts.values());
  }

  getByCategory(category: CommandCategory): Shortcut[] {
    return this.getAll().filter((s) => s.category === category);
  }

  getByScope(scope: ShortcutScope): Shortcut[] {
    return this.getAll().filter(
      (s) => s.scope === scope || s.scope === ShortcutScope.GLOBAL
    );
  }
}
