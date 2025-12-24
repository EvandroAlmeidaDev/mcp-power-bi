/*
*  Dashboard PIB Brasil - Visual Customizado Completo
*  Análise de dados rica com múltiplos indicadores
*/
"use strict";

import powerbi from "powerbi-visuals-api";
import { FormattingSettingsService } from "powerbi-visuals-utils-formattingmodel";
import "./../style/visual.less";

import VisualConstructorOptions = powerbi.extensibility.visual.VisualConstructorOptions;
import VisualUpdateOptions = powerbi.extensibility.visual.VisualUpdateOptions;
import IVisual = powerbi.extensibility.visual.IVisual;

import { VisualFormattingSettingsModel } from "./settings";

interface DataPoint {
    category: string;
    region: string;
    pibTotal: number;
    pibPerCapita: number;
    population: number;
    count: number;
}

export class Visual implements IVisual {
    private target: HTMLElement;
    private formattingSettings: VisualFormattingSettingsModel;
    private formattingSettingsService: FormattingSettingsService;
    private isDarkMode: boolean = true;
    private data: DataPoint[] = [];
    private sortField: string = 'pibTotal';
    private sortAsc: boolean = false;
    private activeRegion: string = 'all';

    constructor(options: VisualConstructorOptions) {
        console.log('Dashboard PIB Brasil v2.0 - Inicializando...');
        this.formattingSettingsService = new FormattingSettingsService();
        this.target = options.element;
        this.render();
    }

    private render(): void {
        this.target.innerHTML = `
        <div class="dashboard ${this.isDarkMode ? 'dark-mode' : 'light-mode'}">
            <header class="header">
                <div class="header-main">
                    <h1>Dashboard PIB Brasil</h1>
                    <p class="subtitle">Analise economica completa</p>
                </div>
                <div class="header-actions">
                    <button class="theme-toggle" id="themeToggle">
                        <span class="theme-icon">${this.isDarkMode ? '🌙' : '☀️'}</span>
                        <span>${this.isDarkMode ? 'Escuro' : 'Claro'}</span>
                    </button>
                </div>
            </header>

            <div class="kpi-grid" id="kpiGrid">
                <div class="kpi-card"><div class="kpi-label">Carregando...</div></div>
            </div>

            <div class="filters" id="regionFilters"></div>

            <div class="content-grid">
                <div class="chart-section">
                    <div class="section-header">
                        <h3>Top 10 - PIB per Capita</h3>
                    </div>
                    <div class="bar-chart" id="chartPibPerCapita"></div>
                </div>
                <div class="chart-section">
                    <div class="section-header">
                        <h3>Top 10 - PIB Total</h3>
                    </div>
                    <div class="bar-chart" id="chartPibTotal"></div>
                </div>
            </div>

            <div class="table-section">
                <div class="section-header">
                    <h3>Dados Detalhados</h3>
                    <span class="record-count" id="recordCount">0 registros</span>
                </div>
                <table id="dataTable">
                    <thead>
                        <tr>
                            <th class="sortable" data-field="category">Nome</th>
                            <th class="sortable" data-field="region">Regiao</th>
                            <th class="sortable" data-field="pibTotal">PIB Total</th>
                            <th class="sortable" data-field="pibPerCapita">PIB/Capita</th>
                            <th class="sortable" data-field="population">Populacao</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody"></tbody>
                </table>
            </div>

            <div class="insights-section" id="insights"></div>
        </div>
        `;
        this.attachEvents();
    }

    private attachEvents(): void {
        // Theme toggle
        this.target.querySelector('#themeToggle')?.addEventListener('click', () => {
            this.isDarkMode = !this.isDarkMode;
            this.render();
            this.updateVisuals();
        });

        // Table sorting
        this.target.querySelectorAll('th.sortable').forEach(th => {
            th.addEventListener('click', (e) => {
                const field = (e.target as HTMLElement).getAttribute('data-field') || 'pibTotal';
                if (this.sortField === field) {
                    this.sortAsc = !this.sortAsc;
                } else {
                    this.sortField = field;
                    this.sortAsc = false;
                }
                this.updateTable();
            });
        });
    }

    public update(options: VisualUpdateOptions): void {
        this.formattingSettings = this.formattingSettingsService.populateFormattingSettingsModel(
            VisualFormattingSettingsModel,
            options.dataViews?.[0]
        );

        const dataView = options.dataViews?.[0];
        if (!dataView?.categorical) {
            this.showEmptyState();
            return;
        }

        this.extractData(dataView);
        this.updateVisuals();
    }

    private extractData(dataView: powerbi.DataView): void {
        const categorical = dataView.categorical;
        if (!categorical) return;

        const categories = categorical.categories || [];
        const values = categorical.values || [];

        // Mapeia colunas
        const categoryCol = categories.find(c => c.source.roles?.['category']);
        const regionCol = categories.find(c => c.source.roles?.['region']);

        const pibTotalCol = values.find(v => v.source.roles?.['pibTotal']);
        const pibPerCapitaCol = values.find(v => v.source.roles?.['pibPerCapita']);
        const populationCol = values.find(v => v.source.roles?.['population']);
        const countCol = values.find(v => v.source.roles?.['count']);

        const length = categoryCol?.values?.length || regionCol?.values?.length || 0;
        this.data = [];

        for (let i = 0; i < length; i++) {
            this.data.push({
                category: String(categoryCol?.values?.[i] || regionCol?.values?.[i] || 'N/A'),
                region: String(regionCol?.values?.[i] || categoryCol?.values?.[i] || 'N/A'),
                pibTotal: Number(pibTotalCol?.values?.[i] || 0),
                pibPerCapita: Number(pibPerCapitaCol?.values?.[i] || pibTotalCol?.values?.[i] || 0),
                population: Number(populationCol?.values?.[i] || 0),
                count: Number(countCol?.values?.[i] || 1)
            });
        }

        console.log('Dados extraidos:', this.data.length, 'registros');
    }

    private updateVisuals(): void {
        this.updateKPIs();
        this.updateFilters();
        this.updateCharts();
        this.updateTable();
        this.updateInsights();
    }

    private updateKPIs(): void {
        const grid = this.target.querySelector('#kpiGrid');
        if (!grid) return;

        const filtered = this.getFilteredData();

        const totalPib = filtered.reduce((s, d) => s + d.pibTotal, 0);
        const avgPibPC = filtered.length > 0 ? filtered.reduce((s, d) => s + d.pibPerCapita, 0) / filtered.length : 0;
        const totalPop = filtered.reduce((s, d) => s + d.population, 0);
        const totalCount = filtered.length;
        const maxPibPC = filtered.length > 0 ? Math.max(...filtered.map(d => d.pibPerCapita)) : 0;
        const minPibPC = filtered.length > 0 ? Math.min(...filtered.filter(d => d.pibPerCapita > 0).map(d => d.pibPerCapita)) : 0;

        grid.innerHTML = `
            <div class="kpi-card kpi-highlight">
                <div class="kpi-icon">💰</div>
                <div class="kpi-content">
                    <div class="kpi-value">${this.formatCurrency(totalPib)}</div>
                    <div class="kpi-label">PIB Total Agregado</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">📊</div>
                <div class="kpi-content">
                    <div class="kpi-value">${this.formatCurrency(avgPibPC)}</div>
                    <div class="kpi-label">PIB per Capita Medio</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">👥</div>
                <div class="kpi-content">
                    <div class="kpi-value">${this.formatNumber(totalPop)}</div>
                    <div class="kpi-label">Populacao Total</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">🏙️</div>
                <div class="kpi-content">
                    <div class="kpi-value">${this.formatNumber(totalCount)}</div>
                    <div class="kpi-label">Total de Registros</div>
                </div>
            </div>
            <div class="kpi-card kpi-success">
                <div class="kpi-icon">🏆</div>
                <div class="kpi-content">
                    <div class="kpi-value">${this.formatCurrency(maxPibPC)}</div>
                    <div class="kpi-label">Maior PIB/Capita</div>
                </div>
            </div>
            <div class="kpi-card kpi-warning">
                <div class="kpi-icon">📉</div>
                <div class="kpi-content">
                    <div class="kpi-value">${this.formatCurrency(minPibPC)}</div>
                    <div class="kpi-label">Menor PIB/Capita</div>
                </div>
            </div>
        `;
    }

    private updateFilters(): void {
        const container = this.target.querySelector('#regionFilters');
        if (!container) return;

        const regions = [...new Set(this.data.map(d => d.region))].sort();

        container.innerHTML = `
            <div class="chip ${this.activeRegion === 'all' ? 'active' : ''}" data-region="all">Todos (${this.data.length})</div>
            ${regions.slice(0, 10).map(r => {
            const count = this.data.filter(d => d.region === r).length;
            return `<div class="chip ${this.activeRegion === r ? 'active' : ''}" data-region="${r}">${r} (${count})</div>`;
        }).join('')}
        `;

        container.querySelectorAll('.chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                this.activeRegion = (e.target as HTMLElement).getAttribute('data-region') || 'all';
                this.updateVisuals();
            });
        });
    }

    private updateCharts(): void {
        const filtered = this.getFilteredData();

        // Top PIB per Capita
        const topPibPC = [...filtered].sort((a, b) => b.pibPerCapita - a.pibPerCapita).slice(0, 10);
        this.renderBarChart('chartPibPerCapita', topPibPC, 'pibPerCapita', '#2563eb');

        // Top PIB Total
        const topPibTotal = [...filtered].sort((a, b) => b.pibTotal - a.pibTotal).slice(0, 10);
        this.renderBarChart('chartPibTotal', topPibTotal, 'pibTotal', '#22c55e');
    }

    private renderBarChart(containerId: string, data: DataPoint[], field: 'pibTotal' | 'pibPerCapita', color: string): void {
        const container = this.target.querySelector(`#${containerId}`);
        if (!container || data.length === 0) return;

        const maxVal = Math.max(...data.map(d => d[field]));

        container.innerHTML = data.map((item, i) => {
            const pct = maxVal > 0 ? (item[field] / maxVal) * 100 : 0;
            return `
                <div class="bar-row" style="animation-delay: ${i * 50}ms">
                    <div class="bar-rank">${i + 1}</div>
                    <div class="bar-name" title="${item.category}">${item.category.substring(0, 20)}</div>
                    <div class="bar-track">
                        <div class="bar-fill" style="width: ${pct}%; background: ${color}">
                            <span class="bar-value">${this.formatCurrency(item[field])}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    private updateTable(): void {
        const tbody = this.target.querySelector('#tableBody');
        const countEl = this.target.querySelector('#recordCount');
        if (!tbody) return;

        let filtered = this.getFilteredData();

        // Sort
        filtered.sort((a, b) => {
            const aVal = a[this.sortField as keyof DataPoint];
            const bVal = b[this.sortField as keyof DataPoint];
            if (typeof aVal === 'number' && typeof bVal === 'number') {
                return this.sortAsc ? aVal - bVal : bVal - aVal;
            }
            return this.sortAsc ? String(aVal).localeCompare(String(bVal)) : String(bVal).localeCompare(String(aVal));
        });

        if (countEl) countEl.textContent = `${filtered.length} registros`;

        tbody.innerHTML = filtered.slice(0, 50).map((d, i) => `
            <tr>
                <td>${d.category}</td>
                <td><span class="region-tag">${d.region}</span></td>
                <td class="num">${this.formatCurrency(d.pibTotal)}</td>
                <td class="num">${this.formatCurrency(d.pibPerCapita)}</td>
                <td class="num">${this.formatNumber(d.population)}</td>
            </tr>
        `).join('');
    }

    private updateInsights(): void {
        const container = this.target.querySelector('#insights');
        if (!container) return;

        const filtered = this.getFilteredData();
        if (filtered.length === 0) return;

        const sorted = [...filtered].sort((a, b) => b.pibPerCapita - a.pibPerCapita);
        const top = sorted[0];
        const bottom = sorted[sorted.length - 1];
        const ratio = bottom.pibPerCapita > 0 ? (top.pibPerCapita / bottom.pibPerCapita).toFixed(1) : 'N/A';

        container.innerHTML = `
            <div class="insight-card">
                <div class="insight-title">💡 Insight Automatico</div>
                <div class="insight-text">
                    <strong>${top.category}</strong> tem o maior PIB per capita (${this.formatCurrency(top.pibPerCapita)}), 
                    enquanto <strong>${bottom.category}</strong> tem o menor (${this.formatCurrency(bottom.pibPerCapita)}).
                    A diferenca entre eles e de <strong>${ratio}x</strong>.
                </div>
            </div>
        `;
    }

    private getFilteredData(): DataPoint[] {
        if (this.activeRegion === 'all') return this.data;
        return this.data.filter(d => d.region === this.activeRegion);
    }

    private showEmptyState(): void {
        const grid = this.target.querySelector('#kpiGrid');
        if (grid) {
            grid.innerHTML = `
                <div class="empty-state">
                    <h3>Arraste campos para os slots:</h3>
                    <ul>
                        <li><strong>Categoria:</strong> nome do municipio/estado</li>
                        <li><strong>Regiao/UF:</strong> UF ou regiao</li>
                        <li><strong>PIB Total:</strong> soma do PIB</li>
                        <li><strong>PIB per Capita:</strong> PIB medio</li>
                        <li><strong>Populacao:</strong> total de habitantes</li>
                    </ul>
                </div>
            `;
        }
    }

    private formatNumber(value: number): string {
        if (value >= 1e9) return `${(value / 1e9).toFixed(1)}B`;
        if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
        if (value >= 1e3) return `${(value / 1e3).toFixed(0)}K`;
        return value.toLocaleString('pt-BR');
    }

    private formatCurrency(value: number): string {
        if (value >= 1e12) return `R$ ${(value / 1e12).toFixed(1)}T`;
        if (value >= 1e9) return `R$ ${(value / 1e9).toFixed(1)}B`;
        if (value >= 1e6) return `R$ ${(value / 1e6).toFixed(1)}M`;
        if (value >= 1e3) return `R$ ${(value / 1e3).toFixed(0)}K`;
        return `R$ ${value.toLocaleString('pt-BR')}`;
    }

    public getFormattingModel(): powerbi.visuals.FormattingModel {
        return this.formattingSettingsService.buildFormattingModel(this.formattingSettings);
    }
}