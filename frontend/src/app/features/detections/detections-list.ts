import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { DetectionService } from '../../core/services/detection';
import { Detection } from '../../core/models/detection';
import { CardComponent } from '../../shared/components/card/card';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state';

@Component({
	selector: 'fp-detections-list',
	standalone: true,
	imports: [
		CommonModule,
		RouterModule,
		MatTableModule,
		MatButtonModule,
		MatIconModule,
		CardComponent,
		LoadingSpinnerComponent,
		EmptyStateComponent
	],
	templateUrl: './detections-list.html',
	styleUrl: './detections-list.scss'
})
export class DetectionsListComponent implements OnInit {
	private readonly detectionService = inject(DetectionService);

	loading = false;
	displayedColumns = ['name', 'file_hash', 'sources', 'actions'];
	data: Detection[] = [];

	ngOnInit(): void {
		this.fetch();
	}

	fetch(): void {
		this.loading = true;
		this.detectionService.list().subscribe({
			next: detections => {
				this.data = detections;
				this.loading = false;
			},
			error: () => {
				this.loading = false;
			}
		});
	}

	getSourcesLabel(det: Detection): string {
		return det.sources.length ? det.sources.join(', ') : '—';
	}

	getStatusLabel(det: Detection): string {
		return det.deleted ? 'Clean' : 'Detected';
	}

	getStatusClass(det: Detection): string {
		return det.deleted ? 'fp-badge fp-badge--success' : 'fp-badge fp-badge--danger';
	}
}