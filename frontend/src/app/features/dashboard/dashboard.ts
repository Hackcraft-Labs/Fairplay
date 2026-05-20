import { Component, OnInit, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { CardComponent } from '../../shared/components/card/card';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state';
import { DetectionService } from '../../core/services/detection';
import { Detection } from '../../core/models/detection';
import { IocService } from '../../core/services/ioc';
import { Ioc } from '../../core/models/ioc';
import { RefreshService } from '../../core/services/refresh';
import { forkJoin } from 'rxjs';

@Component({
	selector: 'fp-dashboard',
	standalone: true,
	imports: [CommonModule, MatIconModule, CardComponent, LoadingSpinnerComponent, EmptyStateComponent],
	templateUrl: './dashboard.html',
	styleUrl: './dashboard.scss'
})
export class DashboardComponent implements OnInit {
	private readonly detectionService = inject(DetectionService);
	private readonly iocService = inject(IocService);
	private readonly refreshService = inject(RefreshService);

	loading = false;
	detectionsCount = 0;
	iocsCount = 0;
	activeIocsCount = 0;
	latestDetections: Detection[] = [];

	constructor() {
		this.refreshService
			.afterDataChanged()
			.pipe(takeUntilDestroyed())
			.subscribe(() => this.load());
	}

	ngOnInit(): void {
		this.load();
	}

	private load(): void {
		this.loading = true;
		forkJoin({
			detections: this.detectionService.list(),
			iocs: this.iocService.list()
		}).subscribe({
			next: ({ detections, iocs }) => {
				this.detectionsCount = detections.length;
				this.latestDetections = detections.slice(0, 5);
				this.iocsCount = iocs.length;
				this.activeIocsCount = iocs.filter(ioc => this.isIocActive(ioc)).length;
				this.loading = false;
			},
			error: () => {
				this.loading = false;
			}
		});
	}

	private isIocActive(ioc: Ioc): boolean {
		return ioc.active !== false;
	}

	getStatusLabel(det: Detection): string {
		return det.deleted ? 'Clean' : 'Detected';
	}

	getStatusClass(det: Detection): string {
		return det.deleted ? 'fp-badge fp-badge--success' : 'fp-badge fp-badge--danger';
	}
}