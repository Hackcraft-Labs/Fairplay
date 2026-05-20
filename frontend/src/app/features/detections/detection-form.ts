import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { DetectionService } from '../../core/services/detection';
import { Detection } from '../../core/models/detection';
import { CardComponent } from '../../shared/components/card/card';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner';

@Component({
	selector: 'fp-detection-form',
	standalone: true,
	imports: [
		CommonModule,
		ReactiveFormsModule,
		RouterModule,
		MatFormFieldModule,
		MatInputModule,
		MatButtonModule,
		MatSlideToggleModule,
		CardComponent,
		LoadingSpinnerComponent
	],
	templateUrl: './detection-form.html',
	styleUrl: './detection-form.scss'
})
export class DetectionFormComponent implements OnInit {
	private readonly fb = inject(FormBuilder);
	private readonly route = inject(ActivatedRoute);
	private readonly router = inject(Router);
	private readonly detectionService = inject(DetectionService);

	loading = false;
	isEditMode = false;

	form = this.fb.group({
		name: ['', [Validators.required]],
		file_hash: ['', [Validators.required]],
		deleted: [false]
	});

	get fileHashParam(): string | null {
		return this.route.snapshot.paramMap.get('fileHash');
	}

	ngOnInit(): void {
		const existingHash = this.fileHashParam;
		this.isEditMode = !!existingHash;

		if (this.isEditMode && existingHash) {
			this.loading = true;
			this.detectionService.get(existingHash).subscribe({
				next: det => {
					this.form.patchValue({
						name: det.name,
						file_hash: det.file_hash,
						deleted: det.deleted ?? false
					});
					this.loading = false;
				},
				error: () => {
					this.loading = false;
					this.router.navigate(['/detections']);
				}
			});
		}
	}

	submit(): void {
		if (this.form.invalid) {
			this.form.markAllAsTouched();
			return;
		}

		const payload: Detection = {
			name: this.form.value.name!,
			file_hash: this.form.value.file_hash!,
			sources: [],
			initial_detection_time: {
				unix: '0',
				text: ''
			},
			extra_info: {},
			deleted: this.form.value.deleted ?? false
		};

		this.loading = true;

		if (this.isEditMode && this.fileHashParam) {
			this.detectionService.update(this.fileHashParam, payload).subscribe({
				next: det => this.router.navigate(['/detections', det.file_hash]),
				error: () => (this.loading = false)
			});
		} 
		else {
			this.detectionService.create(payload).subscribe({
				next: det => this.router.navigate(['/detections', det.file_hash]),
				error: () => (this.loading = false)
			});
		}
	}
}