/// <reference types="cypress" />

describe('Explorer', () => {
  beforeEach(() => {
    cy.visit('/explorer/', { timeout: 20000 });
  });

  it('loads successfully', () => {
    cy.get('h1, h2').should('exist');
    cy.title().should('not.be.empty');
  });

  it('shows live block height', () => {
    cy.get('body').should('contain', '#');
  });

  it('shows peer count', () => {
    cy.get('body').should('contain', 'peer');
  });

  it('shows validator information', () => {
    cy.get('body').should('contain', 'validator');
  });
});

describe('Status Page', () => {
  it('shows all health metrics', () => {
    cy.visit('/status/');
    cy.get('.value', { timeout: 10000 }).should('have.length.at.least', 3);
    cy.get('.card').should('contain', 'BLOCK HEIGHT');
    cy.get('.card').should('contain', 'Peers');
  });

  it('auto-refreshes every 30 seconds', () => {
    cy.visit('/status/');
    cy.get('meta[http-equiv="refresh"]').should('have.attr', 'content', '30');
  });
});
