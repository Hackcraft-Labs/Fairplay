import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { DetectionService } from '../../core/services/detection';
import { Detection } from '../../core/models/detection';
import { CardComponent } from '../../shared/components/card/card';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner';

@Component({
	selector: 'fp-detection-detail',
	standalone: true,
	imports: [
		CommonModule,
		RouterModule,
		MatChipsModule,
		MatButtonModule,
		MatIconModule,
		CardComponent,
		LoadingSpinnerComponent
	],
	templateUrl: './detection-detail.html',
	styleUrl: './detection-detail.scss'
})
export class DetectionDetailComponent implements OnInit {
	private readonly route = inject(ActivatedRoute);
	private readonly router = inject(Router);
	private readonly detectionService = inject(DetectionService);

	detection?: Detection;
	loading = false;

	get fileHash(): string | null {
		return this.route.snapshot.paramMap.get('fileHash');
	}

	ngOnInit(): void {
		const hash = this.fileHash;
		if (!hash) {
			this.router.navigate(['/detections']);
			return;
		}

		this.loading = true;
			this.detectionService.get(hash).subscribe({
			next: det => {
				this.detection = det;
				this.loading = false;
			},
			error: () => {
				this.loading = false;
				this.router.navigate(['/detections']);
			}
		});
	}

	delete(): void {
		if (!this.detection || !confirm('Delete this detection?')) {
			return;
		}

		this.loading = true;
		this.detectionService.delete(this.detection.file_hash).subscribe({
			next: () => this.router.navigate(['/detections']),
			error: () => (this.loading = false)
		});
	}

	extraInfoEntries(det: Detection) {
		return Object.entries(det.extra_info ?? {});
	}
}