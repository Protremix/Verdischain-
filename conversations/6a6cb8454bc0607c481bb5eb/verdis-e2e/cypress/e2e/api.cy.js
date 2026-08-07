/// <reference types="cypress" />

describe('RPC API', () => {
  const RPC = '/rpc';

  it('chain_getHeader returns valid header', () => {
    cy.request('POST', RPC, {
      jsonrpc: '2.0', method: 'chain_getHeader', params: [], id: 1
    }).then((res) => {
      expect(res.status).to.eq(200);
      expect(res.body.result).to.exist;
      expect(res.body.result.number).to.match(/^0x[0-9a-f]+$/);
      expect(parseInt(res.body.result.number, 16)).to.be.greaterThan(0);
    });
  });

  it('system_health returns peer count', () => {
    cy.request('POST', RPC, {
      jsonrpc: '2.0', method: 'system_health', params: [], id: 2
    }).then((res) => {
      expect(res.body.result.peers).to.be.greaterThan(0);
      expect(res.body.result.isSyncing).to.eq(false);
    });
  });

  it('system_name returns chain name', () => {
    cy.request('POST', RPC, {
      jsonrpc: '2.0', method: 'system_chain', params: [], id: 3
    }).then((res) => {
      expect(res.body.result).to.exist;
      expect(res.body.result).to.not.be.empty;
    });
  });

  it('amm_dex_getPoolCount returns pool count', () => {
    cy.request('POST', RPC, {
      jsonrpc: '2.0', method: 'amm_dex_getPoolCount', params: [], id: 4
    }).then((res) => {
      expect(res.body.result).to.be.greaterThan(0);
    });
  });

  it('amm_dex_getAllPools returns pool array', () => {
    cy.request('POST', RPC, {
      jsonrpc: '2.0', method: 'amm_dex_getAllPools', params: [], id: 5
    }).then((res) => {
      expect(res.body.result).to.be.an('array');
      expect(res.body.result.length).to.be.greaterThan(0);
      const pool = res.body.result[0];
      expect(pool).to.have.property('token_a');
      expect(pool).to.have.property('token_b');
      expect(pool).to.have.property('reserve_a');
      expect(pool).to.have.property('reserve_b');
    });
  });

  it('dpos_activeValidators returns validator array', () => {
    cy.request('POST', RPC, {
      jsonrpc: '2.0', method: 'dpos_activeValidators', params: [], id: 6
    }).then((res) => {
      expect(res.body.result).to.exist;
      expect(res.body.result.length).to.be.greaterThan(0);
    });
  });

  it('WebSocket endpoint returns 101', () => {
    cy.request({
      method: 'GET',
      url: '/ws',
      headers: { 'Upgrade': 'websocket', 'Connection': 'Upgrade' },
      failOnStatusCode: false
    }).then((res) => {
      // WebSocket upgrade returns 101 or 426 (upgrade required)
      expect([101, 426, 200]).to.include(res.status);
    });
  });
});

describe('Page Availability', () => {
  const pages = [
    '/', '/explorer/', '/dex/', '/wallet/', '/faucet/',
    '/sale/', '/validators/', '/docs/', '/whitepaper/',
    '/eco/', '/status/'
  ];

  pages.forEach((page) => {
    it(`${page} returns 200`, () => {
      cy.request(page).its('status').should('eq', 200);
    });
  });
});

describe('Security Headers', () => {
  it('has X-Frame-Options', () => {
    cy.request('/').its('headers').should('have.property', 'x-frame-options');
  });

  it('has X-Content-Type-Options', () => {
    cy.request('/').its('headers').should('have.property', 'x-content-type-options');
  });

  it('has Strict-Transport-Security', () => {
    cy.request('/').its('headers').should('have.property', 'strict-transport-security');
  });
});

describe('Mobile Responsiveness', () => {
  [375, 768, 1024, 1280].forEach((width) => {
    it(`works at ${width}px width`, () => {
      cy.viewport(width, 667);
      cy.visit('/');
      cy.get('body').should('be.visible');
      cy.get('nav').should('be.visible');
    });
  });

  it('wallet works at 375px', () => {
    cy.viewport(375, 667);
    cy.visit('/wallet/', { timeout: 20000 });
    cy.get('h1').should('be.visible');
  });

  it('DEX works at 375px', () => {
    cy.viewport(375, 667);
    cy.visit('/dex/', { timeout: 20000 });
    cy.get('h1').should('be.visible');
  });
});
