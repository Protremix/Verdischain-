/// <reference types="cypress" />

describe('Landing Page', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('loads successfully', () => {
    cy.get('h1, h2').should('exist');
    cy.title().should('not.be.empty');
  });

  it('has navigation links', () => {
    cy.get('nav a').should('have.length.at.least', 5);
    cy.get('nav a').first().should('be.visible');
  });

  it('all nav links resolve', () => {
    cy.get('nav a').each(($el) => {
      const href = $el.attr('href');
      if (href && href.startsWith('/') && !href.startsWith('//')) {
        cy.request(href).its('status').should('eq', 200);
      }
    });
  });

  it('shows live block height', () => {
    cy.get('body').should('contain', '#');
  });

  it('has VRDX token reference', () => {
    cy.get('body').should('contain', 'VRDX');
  });

  it('meta description exists', () => {
    cy.get('meta[name="description"]').should('exist');
  });

  it('viewport meta tag exists', () => {
    cy.get('meta[name="viewport"]').should('exist');
  });
});
