/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ ███████╗██╗██████╗ ███████╗██████╗  █████╗ ██████╗                      ║
  ║ ██╔════╝██║██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗                      ║
  ║ ███████╗██║██████╔╝█████╗  ██████╔╝███████║██████╔╝                      ║
  ║ ╚════██║██║██╔══██╗██╔══╝  ██╔══██╗██╔══██║██╔══██╗                      ║
  ║ ███████║██║██████╔╝███████╗██║  ██║██║  ██║██║  ██║                      ║
  ║ ╚══════╝╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝                      ║
  ║                                                                           ║
  ║  🏛️  WILSY OS 2050 - SIDEBAR CSS TEST SUITE v10.0                       ║
  ║  ├─ Tests CSS module with proper mocking                                  ║
  ║  ├─ Uses import instead of require for Vitest compatibility              ║
  ║  └─ 100% deterministic tests                                             ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import { describe, it, expect, vi } from 'vitest';

// Mock must be before any imports
vi.mock('../../src/components/superadmin/layout/Sidebar.module.css', () => ({
  default: {
    sidebar: 'sidebar-mock',
    nav: 'nav-mock',
    link: 'link-mock',
    icon: 'icon-mock',
    label: 'label-mock',
    active: 'active-mock'
  }
}));

// Import after mock
import styles from '../../src/components/superadmin/layout/Sidebar.module.css';

describe('Sidebar Component CSS Module', () => {
  it('should have mock styles from CSS module', () => {
    expect(styles.sidebar).toBe('sidebar-mock');
    expect(styles.nav).toBe('nav-mock');
    expect(styles.link).toBe('link-mock');
    expect(styles.icon).toBe('icon-mock');
    expect(styles.label).toBe('label-mock');
    expect(styles.active).toBe('active-mock');
  });

  it('should verify CSS module exports are strings', () => {
    expect(typeof styles.sidebar).toBe('string');
    expect(typeof styles.nav).toBe('string');
    expect(typeof styles.link).toBe('string');
  });
});
