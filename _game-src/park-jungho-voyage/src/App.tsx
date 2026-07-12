"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import * as THREE from "three";

type GameMode = "intro" | "playing" | "paused" | "won" | "lost";

type Particle = {
  mesh: THREE.Mesh;
  velocity: THREE.Vector3;
  life: number;
  maxLife: number;
};

type Collectible = {
  group: THREE.Group;
  collected: boolean;
  label: string;
};

type Obstacle = {
  group: THREE.Group;
  radius: number;
  hitUntil: number;
};

const COURSE_LENGTH = 1500;
const TOPICS = ["금리", "환율", "물가", "증시", "부동산", "AI 경제"];

const clamp = (value: number, min: number, max: number) =>
  Math.min(max, Math.max(min, value));

function createTextSprite(
  text: string,
  foreground = "#08253f",
  background = "#fff4c7",
  scale = 1,
) {
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 160;
  const context = canvas.getContext("2d")!;
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = background;
  context.beginPath();
  context.roundRect(16, 18, 480, 124, 42);
  context.fill();
  context.strokeStyle = "rgba(255,255,255,.72)";
  context.lineWidth = 5;
  context.stroke();
  context.fillStyle = foreground;
  context.font = "800 54px Arial, sans-serif";
  context.textAlign = "center";
  context.textBaseline = "middle";
  context.fillText(text, 256, 82);

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  const material = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
    depthWrite: false,
  });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(7.2 * scale, 2.25 * scale, 1);
  return sprite;
}

function makeHull() {
  const geometry = new THREE.BufferGeometry();
  const vertices = new Float32Array([
    -1.6, 0, 2.6, 1.6, 0, 2.6, 1.1, -0.8, 1.8,
    -1.6, 0, 2.6, 1.1, -0.8, 1.8, -1.1, -0.8, 1.8,
    -1.1, -0.8, 1.8, 1.1, -0.8, 1.8, 0.75, -0.9, -2.4,
    -1.1, -0.8, 1.8, 0.75, -0.9, -2.4, -0.75, -0.9, -2.4,
    -1.6, 0, 2.6, -1.1, -0.8, 1.8, -0.75, -0.9, -2.4,
    -1.6, 0, 2.6, -0.75, -0.9, -2.4, -1.05, 0, -2.7,
    1.6, 0, 2.6, 1.05, 0, -2.7, 0.75, -0.9, -2.4,
    1.6, 0, 2.6, 0.75, -0.9, -2.4, 1.1, -0.8, 1.8,
    -1.6, 0, 2.6, -1.05, 0, -2.7, 1.05, 0, -2.7,
    -1.6, 0, 2.6, 1.05, 0, -2.7, 1.6, 0, 2.6,
    -0.75, -0.9, -2.4, 0.75, -0.9, -2.4, 1.1, -0.8, 1.8,
    -0.75, -0.9, -2.4, 1.1, -0.8, 1.8, -1.1, -0.8, 1.8,
  ]);
  geometry.setAttribute("position", new THREE.BufferAttribute(vertices, 3));
  geometry.computeVertexNormals();
  return geometry;
}

function buildBoat() {
  const boat = new THREE.Group();
  const hull = new THREE.Mesh(
    makeHull(),
    new THREE.MeshStandardMaterial({
      color: 0x083d5d,
      roughness: 0.38,
      metalness: 0.1,
    }),
  );
  hull.castShadow = true;
  boat.add(hull);

  const stripe = new THREE.Mesh(
    new THREE.BoxGeometry(2.35, 0.18, 4.8),
    new THREE.MeshStandardMaterial({ color: 0xffc93c, roughness: 0.45 }),
  );
  stripe.position.y = 0.12;
  stripe.castShadow = true;
  boat.add(stripe);

  const deck = new THREE.Mesh(
    new THREE.BoxGeometry(2.2, 0.22, 3.7),
    new THREE.MeshStandardMaterial({ color: 0xf1dfb5, roughness: 0.82 }),
  );
  deck.position.y = 0.35;
  deck.castShadow = true;
  boat.add(deck);

  const cabin = new THREE.Mesh(
    new THREE.BoxGeometry(1.65, 1.05, 1.65),
    new THREE.MeshStandardMaterial({ color: 0xf5f0df, roughness: 0.5 }),
  );
  cabin.position.set(0, 0.95, 0.35);
  cabin.castShadow = true;
  boat.add(cabin);

  const windowMaterial = new THREE.MeshStandardMaterial({
    color: 0x7fe6ff,
    emissive: 0x0f6885,
    emissiveIntensity: 0.4,
    metalness: 0.25,
    roughness: 0.1,
  });
  const frontWindow = new THREE.Mesh(
    new THREE.BoxGeometry(1.18, 0.42, 0.05),
    windowMaterial,
  );
  frontWindow.position.set(0, 1.08, -0.5);
  boat.add(frontWindow);

  const roof = new THREE.Mesh(
    new THREE.BoxGeometry(1.95, 0.14, 1.9),
    new THREE.MeshStandardMaterial({ color: 0xffc93c, roughness: 0.45 }),
  );
  roof.position.set(0, 1.55, 0.35);
  boat.add(roof);

  const mast = new THREE.Mesh(
    new THREE.CylinderGeometry(0.055, 0.075, 3.2, 10),
    new THREE.MeshStandardMaterial({ color: 0xe9edf0, metalness: 0.65 }),
  );
  mast.position.set(0, 2.25, 0.15);
  boat.add(mast);

  const flag = new THREE.Mesh(
    new THREE.PlaneGeometry(1.35, 0.67),
    new THREE.MeshStandardMaterial({
      color: 0xff5547,
      side: THREE.DoubleSide,
      roughness: 0.55,
    }),
  );
  flag.position.set(0.69, 3.15, 0.15);
  boat.add(flag);

  const captain = new THREE.Group();
  const body = new THREE.Mesh(
    new THREE.CapsuleGeometry(0.19, 0.35, 4, 8),
    new THREE.MeshStandardMaterial({ color: 0xff715b }),
  );
  body.position.y = 0.25;
  const head = new THREE.Mesh(
    new THREE.SphereGeometry(0.2, 16, 12),
    new THREE.MeshStandardMaterial({ color: 0xffd0ad }),
  );
  head.position.y = 0.72;
  const cap = new THREE.Mesh(
    new THREE.SphereGeometry(0.21, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2),
    new THREE.MeshStandardMaterial({ color: 0x092d46 }),
  );
  cap.position.y = 0.84;
  captain.add(body, head, cap);
  captain.position.set(0, 1.55, -0.05);
  boat.add(captain);

  const name = createTextSprite("박정호호", "#ffffff", "#ff574c", 0.52);
  name.position.set(0, 1.05, 2.1);
  boat.add(name);

  boat.rotation.y = Math.PI;
  boat.scale.setScalar(0.9);
  return boat;
}

function buildRock(scale: number, seed: number) {
  const group = new THREE.Group();
  const material = new THREE.MeshStandardMaterial({
    color: seed % 2 ? 0x394956 : 0x52626b,
    roughness: 1,
  });
  for (let i = 0; i < 3; i += 1) {
    const rock = new THREE.Mesh(
      new THREE.DodecahedronGeometry(scale * (0.55 + i * 0.12), 0),
      material,
    );
    rock.position.set((i - 1) * scale * 0.55, i * 0.12, (i % 2) * 0.3);
    rock.rotation.set(seed * 0.17 + i, seed * 0.29, i * 0.43);
    rock.castShadow = true;
    group.add(rock);
  }
  const warning = createTextSprite("경제 암초", "#ffffff", "#ff5a4f", 0.42);
  warning.position.y = scale * 1.5 + 1.5;
  group.add(warning);
  return group;
}

function buildCollectible(label: string) {
  const group = new THREE.Group();
  const ring = new THREE.Mesh(
    new THREE.TorusGeometry(0.8, 0.15, 12, 28),
    new THREE.MeshStandardMaterial({
      color: 0xffd14a,
      emissive: 0xe78600,
      emissiveIntensity: 1.4,
      metalness: 0.55,
      roughness: 0.22,
    }),
  );
  ring.rotation.x = Math.PI / 2;
  const core = new THREE.Mesh(
    new THREE.OctahedronGeometry(0.38, 0),
    new THREE.MeshStandardMaterial({
      color: 0xffffd6,
      emissive: 0xffa51f,
      emissiveIntensity: 1.8,
      roughness: 0.1,
    }),
  );
  const title = createTextSprite(label, "#08253f", "#fff4c7", 0.48);
  title.position.y = 1.45;
  group.add(ring, core, title);
  group.position.y = 1.15;
  return group;
}

function buildLighthouse() {
  const group = new THREE.Group();
  const island = new THREE.Mesh(
    new THREE.CylinderGeometry(8, 10, 2.3, 20),
    new THREE.MeshStandardMaterial({ color: 0x6d8860, roughness: 0.95 }),
  );
  island.position.y = -0.4;
  island.castShadow = true;
  group.add(island);

  const tower = new THREE.Mesh(
    new THREE.CylinderGeometry(1.1, 2.2, 12, 22),
    new THREE.MeshStandardMaterial({ color: 0xf4ead5, roughness: 0.65 }),
  );
  tower.position.y = 6.5;
  tower.castShadow = true;
  group.add(tower);

  for (let i = 0; i < 3; i += 1) {
    const stripe = new THREE.Mesh(
      new THREE.CylinderGeometry(1.35 + i * 0.22, 1.48 + i * 0.22, 1.35, 22),
      new THREE.MeshStandardMaterial({ color: 0xff5a4f, roughness: 0.55 }),
    );
    stripe.position.y = 3.3 + i * 3.2;
    group.add(stripe);
  }

  const lantern = new THREE.Mesh(
    new THREE.CylinderGeometry(1.3, 1.3, 1.55, 16),
    new THREE.MeshStandardMaterial({
      color: 0xffec9c,
      emissive: 0xffa300,
      emissiveIntensity: 2.6,
      transparent: true,
      opacity: 0.94,
    }),
  );
  lantern.position.y = 13.1;
  group.add(lantern);

  const roof = new THREE.Mesh(
    new THREE.ConeGeometry(1.75, 1.3, 18),
    new THREE.MeshStandardMaterial({ color: 0x123d58, roughness: 0.55 }),
  );
  roof.position.y = 14.5;
  group.add(roof);

  const light = new THREE.PointLight(0xffc846, 6, 65, 1.2);
  light.position.y = 13.2;
  group.add(light);

  const beam = new THREE.Mesh(
    new THREE.ConeGeometry(5.5, 48, 24, 1, true),
    new THREE.MeshBasicMaterial({
      color: 0xffe99a,
      transparent: true,
      opacity: 0.12,
      side: THREE.DoubleSide,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    }),
  );
  beam.rotation.z = -Math.PI / 2;
  beam.position.set(24, 13.2, 0);
  beam.name = "beacon";
  group.add(beam);

  const label = createTextSprite("지식의 등대", "#08253f", "#ffd34e", 0.95);
  label.position.y = 18;
  group.add(label);
  return group;
}

class SoundEngine {
  context: AudioContext | null = null;
  master: GainNode | null = null;
  ambient: AudioBufferSourceNode | null = null;
  ambientGain: GainNode | null = null;
  timer: number | null = null;
  enabled = true;
  note = 0;

  init() {
    if (this.context) {
      void this.context.resume();
      return;
    }
    const AudioCtor = window.AudioContext ||
      (window as typeof window & { webkitAudioContext?: typeof AudioContext })
        .webkitAudioContext;
    if (!AudioCtor) return;
    this.context = new AudioCtor();
    this.master = this.context.createGain();
    this.master.gain.value = 0.55;
    this.master.connect(this.context.destination);
    this.startAmbient();
  }

  setEnabled(enabled: boolean) {
    this.enabled = enabled;
    if (this.master && this.context) {
      this.master.gain.setTargetAtTime(
        enabled ? 0.55 : 0,
        this.context.currentTime,
        0.04,
      );
    }
  }

  tone(
    frequency: number,
    duration: number,
    type: OscillatorType = "sine",
    volume = 0.12,
    delay = 0,
  ) {
    if (!this.context || !this.master || !this.enabled) return;
    const oscillator = this.context.createOscillator();
    const gain = this.context.createGain();
    const start = this.context.currentTime + delay;
    oscillator.type = type;
    oscillator.frequency.setValueAtTime(frequency, start);
    gain.gain.setValueAtTime(0.001, start);
    gain.gain.exponentialRampToValueAtTime(volume, start + 0.025);
    gain.gain.exponentialRampToValueAtTime(0.001, start + duration);
    oscillator.connect(gain);
    gain.connect(this.master);
    oscillator.start(start);
    oscillator.stop(start + duration + 0.05);
  }

  startMusic() {
    if (this.timer !== null) return;
    const scale = [196, 246.94, 293.66, 392, 329.63, 293.66, 246.94, 293.66];
    this.timer = window.setInterval(() => {
      if (!this.enabled) return;
      const root = scale[this.note % scale.length];
      this.tone(root, 0.48, "triangle", 0.055);
      if (this.note % 2 === 0) this.tone(root * 2, 0.18, "sine", 0.035, 0.16);
      if (this.note % 4 === 0) this.tone(root / 2, 0.72, "sine", 0.04);
      this.note += 1;
    }, 520);
  }

  startAmbient() {
    if (!this.context || !this.master || this.ambient) return;
    const length = this.context.sampleRate * 2;
    const buffer = this.context.createBuffer(1, length, this.context.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < length; i += 1) {
      data[i] = (Math.random() * 2 - 1) * (0.35 + Math.sin(i / 9000) * 0.1);
    }
    const source = this.context.createBufferSource();
    const filter = this.context.createBiquadFilter();
    const gain = this.context.createGain();
    filter.type = "lowpass";
    filter.frequency.value = 430;
    gain.gain.value = 0.045;
    source.buffer = buffer;
    source.loop = true;
    source.connect(filter);
    filter.connect(gain);
    gain.connect(this.master);
    source.start();
    this.ambient = source;
    this.ambientGain = gain;
  }

  pickup(combo: number) {
    const lift = Math.min(combo, 5) * 25;
    this.tone(660 + lift, 0.18, "sine", 0.14);
    this.tone(880 + lift, 0.28, "triangle", 0.1, 0.09);
  }

  crash() {
    if (!this.context || !this.master || !this.enabled) return;
    const length = Math.floor(this.context.sampleRate * 0.32);
    const buffer = this.context.createBuffer(1, length, this.context.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < length; i += 1) {
      data[i] = (Math.random() * 2 - 1) * (1 - i / length);
    }
    const source = this.context.createBufferSource();
    const filter = this.context.createBiquadFilter();
    const gain = this.context.createGain();
    filter.type = "lowpass";
    filter.frequency.value = 380;
    gain.gain.value = 0.45;
    source.buffer = buffer;
    source.connect(filter);
    filter.connect(gain);
    gain.connect(this.master);
    source.start();
    this.tone(80, 0.38, "sawtooth", 0.14);
  }

  launch() {
    [392, 523.25, 659.25, 783.99].forEach((note, index) =>
      this.tone(note, 0.28, "triangle", 0.1, index * 0.1),
    );
  }

  finish() {
    [523.25, 659.25, 783.99, 1046.5].forEach((note, index) =>
      this.tone(note, 0.65, "triangle", 0.13, index * 0.14),
    );
  }

  dispose() {
    if (this.timer !== null) window.clearInterval(this.timer);
    this.timer = null;
    this.ambient?.stop();
    void this.context?.close();
  }
}

export default function Home() {
  const mountRef = useRef<HTMLDivElement>(null);
  const modeRef = useRef<GameMode>("intro");
  const healthRef = useRef(100);
  const scoreRef = useRef(0);
  const comboRef = useRef(0);
  const collectedRef = useRef(0);
  const resetRef = useRef<(() => void) | null>(null);
  const keyRef = useRef<Record<string, boolean>>({});
  const soundRef = useRef<SoundEngine | null>(null);

  const [mode, setMode] = useState<GameMode>("intro");
  const [score, setScore] = useState(0);
  const [health, setHealth] = useState(100);
  const [progress, setProgress] = useState(0);
  const [collected, setCollected] = useState(0);
  const [combo, setCombo] = useState(0);
  const [soundOn, setSoundOn] = useState(true);
  const [webglUnavailable, setWebglUnavailable] = useState(false);
  const [toast, setToast] = useState("오늘의 경제를 향해 출항 준비!");
  const [speedLabel, setSpeedLabel] = useState("순항");

  const updateMode = useCallback((next: GameMode) => {
    modeRef.current = next;
    setMode(next);
  }, []);

  const startGame = useCallback(() => {
    soundRef.current?.init();
    soundRef.current?.startMusic();
    soundRef.current?.launch();
    resetRef.current?.();
    updateMode("playing");
    setToast("박정호호 출항! 경제 지식을 모아주세요");
  }, [updateMode]);

  const togglePause = useCallback(() => {
    if (modeRef.current === "playing") {
      updateMode("paused");
      setToast("잠시 닻을 내렸습니다");
    } else if (modeRef.current === "paused") {
      updateMode("playing");
      setToast("다시 항해를 시작합니다");
    }
  }, [updateMode]);

  const toggleSound = useCallback(() => {
    const next = !soundOn;
    setSoundOn(next);
    soundRef.current?.setEnabled(next);
  }, [soundOn]);

  const setVirtualKey = useCallback((key: string, active: boolean) => {
    keyRef.current[key] = active;
  }, []);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x8fc8da, 0.0082);

    const camera = new THREE.PerspectiveCamera(
      56,
      mount.clientWidth / mount.clientHeight,
      0.1,
      600,
    );
    camera.position.set(0, 7.5, 13);

    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        powerPreference: "high-performance",
      });
    } catch {
      setWebglUnavailable(true);
      return;
    }
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.12;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    mount.appendChild(renderer.domElement);

    const hemi = new THREE.HemisphereLight(0xc8f5ff, 0x16465c, 2.2);
    scene.add(hemi);
    const sun = new THREE.DirectionalLight(0xfff0c3, 3.2);
    sun.position.set(-35, 48, 24);
    sun.castShadow = true;
    sun.shadow.mapSize.set(1024, 1024);
    sun.shadow.camera.left = -35;
    sun.shadow.camera.right = 35;
    sun.shadow.camera.top = 35;
    sun.shadow.camera.bottom = -35;
    scene.add(sun);

    const skyGeometry = new THREE.SphereGeometry(290, 32, 20);
    const skyMaterial = new THREE.ShaderMaterial({
      side: THREE.BackSide,
      uniforms: {
        topColor: { value: new THREE.Color(0x248ec0) },
        bottomColor: { value: new THREE.Color(0xe4f7f5) },
        offset: { value: 18 },
        exponent: { value: 0.72 },
      },
      vertexShader: `varying vec3 vWorldPosition;
        void main(){ vec4 worldPosition = modelMatrix * vec4(position,1.0); vWorldPosition = worldPosition.xyz; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
      fragmentShader: `uniform vec3 topColor; uniform vec3 bottomColor; uniform float offset; uniform float exponent; varying vec3 vWorldPosition;
        void main(){ float h = normalize(vWorldPosition + offset).y; gl_FragColor = vec4(mix(bottomColor, topColor, max(pow(max(h,0.0), exponent),0.0)),1.0); }`,
    });
    const sky = new THREE.Mesh(skyGeometry, skyMaterial);
    scene.add(sky);

    const sunDisc = new THREE.Mesh(
      new THREE.SphereGeometry(7, 20, 16),
      new THREE.MeshBasicMaterial({ color: 0xffec9a, fog: false }),
    );
    sunDisc.position.set(-65, 54, -180);
    scene.add(sunDisc);

    const waterGeometry = new THREE.PlaneGeometry(110, 310, 44, 130);
    waterGeometry.rotateX(-Math.PI / 2);
    const waterPosition = waterGeometry.attributes.position as THREE.BufferAttribute;
    const baseWater = new Float32Array(waterPosition.array as ArrayLike<number>);
    const waterMaterial = new THREE.MeshPhysicalMaterial({
      color: 0x087ea2,
      roughness: 0.22,
      metalness: 0.08,
      transmission: 0.03,
      transparent: true,
      opacity: 0.98,
      clearcoat: 0.75,
      clearcoatRoughness: 0.26,
      flatShading: true,
    });
    const water = new THREE.Mesh(waterGeometry, waterMaterial);
    water.receiveShadow = true;
    water.position.y = -0.65;
    scene.add(water);

    const boat = buildBoat();
    boat.position.set(0, 0.2, 0);
    scene.add(boat);

    const collectibles: Collectible[] = [];
    const obstacles: Obstacle[] = [];
    const particles: Particle[] = [];
    const world = new THREE.Group();
    scene.add(world);

    for (let i = 0; i < 31; i += 1) {
      const z = -60 - i * 46;
      const topic = TOPICS[i % TOPICS.length];
      const x = [-11, -5, 0, 6, 11][(i * 3 + 1) % 5];
      const collectible = buildCollectible(topic);
      collectible.position.set(x, 0, z - 16);
      world.add(collectible);
      collectibles.push({ group: collectible, collected: false, label: topic });

      if (i < 29) {
        const rockScale = 1.25 + (i % 4) * 0.2;
        const rock = buildRock(rockScale, i);
        const rockX = [-12, -7, -2, 4, 9, 13][(i * 5 + 2) % 6];
        rock.position.set(rockX, -0.05, z);
        world.add(rock);
        obstacles.push({ group: rock, radius: rockScale * 1.15, hitUntil: 0 });
      }
    }

    for (let i = 0; i < 52; i += 1) {
      const z = -20 - i * 29;
      const side = i % 2 === 0 ? -1 : 1;
      const buoy = new THREE.Group();
      const float = new THREE.Mesh(
        new THREE.SphereGeometry(0.38, 12, 10),
        new THREE.MeshStandardMaterial({
          color: side < 0 ? 0xff5b4f : 0xffd042,
          emissive: side < 0 ? 0x5e100b : 0x6e4a00,
          emissiveIntensity: 0.35,
          roughness: 0.5,
        }),
      );
      const pole = new THREE.Mesh(
        new THREE.CylinderGeometry(0.055, 0.055, 1.8, 8),
        new THREE.MeshStandardMaterial({ color: 0xf0f3ef, metalness: 0.2 }),
      );
      pole.position.y = 0.65;
      buoy.add(float, pole);
      buoy.position.set(side * (19 + (i % 3) * 0.5), -0.25, z);
      world.add(buoy);
    }

    const lighthouse = buildLighthouse();
    lighthouse.position.set(0, 0, -COURSE_LENGTH - 38);
    scene.add(lighthouse);

    const clouds: THREE.Group[] = [];
    for (let i = 0; i < 12; i += 1) {
      const cloud = new THREE.Group();
      const cloudMaterial = new THREE.MeshStandardMaterial({
        color: 0xf5fbfc,
        transparent: true,
        opacity: 0.82,
        roughness: 1,
      });
      for (let j = 0; j < 5; j += 1) {
        const puff = new THREE.Mesh(
          new THREE.SphereGeometry(2.1 + (j % 3), 12, 8),
          cloudMaterial,
        );
        puff.position.set(j * 2.2 - 4.4, Math.sin(j) * 0.45, (j % 2) * 1.2);
        cloud.add(puff);
      }
      cloud.position.set(
        (i % 2 ? 1 : -1) * (30 + (i % 4) * 9),
        16 + (i % 3) * 6,
        -i * 135 - 80,
      );
      cloud.scale.setScalar(0.65 + (i % 3) * 0.15);
      scene.add(cloud);
      clouds.push(cloud);
    }

    const spawnParticles = (
      position: THREE.Vector3,
      color: number,
      count: number,
      power = 2.3,
    ) => {
      for (let i = 0; i < count; i += 1) {
        const mesh = new THREE.Mesh(
          new THREE.SphereGeometry(0.07 + Math.random() * 0.09, 7, 5),
          new THREE.MeshBasicMaterial({
            color,
            transparent: true,
            opacity: 0.92,
          }),
        );
        mesh.position.copy(position);
        mesh.position.add(
          new THREE.Vector3(
            (Math.random() - 0.5) * 0.8,
            Math.random() * 0.6,
            (Math.random() - 0.5) * 0.8,
          ),
        );
        scene.add(mesh);
        const maxLife = 0.55 + Math.random() * 0.65;
        particles.push({
          mesh,
          velocity: new THREE.Vector3(
            (Math.random() - 0.5) * power,
            Math.random() * power + 0.5,
            (Math.random() - 0.5) * power,
          ),
          life: maxLife,
          maxLife,
        });
      }
    };

    let lateralVelocity = 0;
    let elapsed = 0;
    let lastFrame = performance.now();
    let lastHudUpdate = 0;
    let lastWake = 0;
    let shake = 0;
    let toastTimeout: number | null = null;

    const showToast = (message: string) => {
      setToast(message);
      if (toastTimeout) window.clearTimeout(toastTimeout);
      toastTimeout = window.setTimeout(() => {
        if (modeRef.current === "playing") setToast("경제의 흐름을 읽으며 전진 중");
      }, 1800);
    };

    const resetGame = () => {
      boat.position.set(0, 0.2, 0);
      boat.rotation.set(0, Math.PI, 0);
      lateralVelocity = 0;
      healthRef.current = 100;
      scoreRef.current = 0;
      comboRef.current = 0;
      collectedRef.current = 0;
      setHealth(100);
      setScore(0);
      setProgress(0);
      setCollected(0);
      setCombo(0);
      collectibles.forEach((item) => {
        item.collected = false;
        item.group.visible = true;
      });
      obstacles.forEach((item) => {
        item.hitUntil = 0;
        item.group.visible = true;
      });
    };
    resetRef.current = resetGame;

    const handleResize = () => {
      if (!mount) return;
      camera.aspect = mount.clientWidth / mount.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(mount.clientWidth, mount.clientHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
    };
    const handleKeyDown = (event: KeyboardEvent) => {
      const key = event.key.toLowerCase();
      keyRef.current[key] = true;
      if (["arrowleft", "arrowright", "arrowup", "arrowdown", " "].includes(key)) {
        event.preventDefault();
      }
      if (key === "p" || key === "escape") togglePause();
      if (key === " " && modeRef.current === "paused") togglePause();
    };
    const handleKeyUp = (event: KeyboardEvent) => {
      keyRef.current[event.key.toLowerCase()] = false;
    };
    window.addEventListener("resize", handleResize);
    window.addEventListener("keydown", handleKeyDown, { passive: false });
    window.addEventListener("keyup", handleKeyUp);

    const clockPosition = new THREE.Vector3();

    const animate = (now: number) => {
      const frameId = requestAnimationFrame(animate);
      mount.dataset.frameId = String(frameId);
      const dt = Math.min((now - lastFrame) / 1000, 0.045);
      lastFrame = now;
      elapsed += dt;

      const positions = waterGeometry.attributes.position as THREE.BufferAttribute;
      for (let i = 0; i < positions.count; i += 1) {
        const x = baseWater[i * 3];
        const z = baseWater[i * 3 + 2];
        positions.setY(
          i,
          baseWater[i * 3 + 1] +
            Math.sin(x * 0.28 + elapsed * 1.45) * 0.22 +
            Math.sin(z * 0.15 + elapsed * 1.1) * 0.26 +
            Math.sin((x + z) * 0.08 + elapsed * 2.1) * 0.1,
        );
      }
      positions.needsUpdate = true;
      waterGeometry.computeVertexNormals();

      const playing = modeRef.current === "playing";
      const pressed = keyRef.current;
      const steer =
        (pressed.arrowleft || pressed.a ? -1 : 0) +
        (pressed.arrowright || pressed.d ? 1 : 0);
      const boost = Boolean(pressed.arrowup || pressed.w);
      const brake = Boolean(pressed.arrowdown || pressed.s);

      if (playing) {
        lateralVelocity += steer * 19 * dt;
        lateralVelocity *= Math.pow(0.035, dt);
        boat.position.x += lateralVelocity * dt;
        if (Math.abs(boat.position.x) > 17.2) {
          boat.position.x = clamp(boat.position.x, -17.2, 17.2);
          lateralVelocity *= -0.28;
        }

        const speed = boost ? 26 : brake ? 9.5 : 17;
        boat.position.z -= speed * dt;
        boat.position.y = 0.18 + Math.sin(elapsed * 2.7) * 0.18;
        boat.rotation.z = THREE.MathUtils.lerp(
          boat.rotation.z,
          -steer * 0.22 - lateralVelocity * 0.025,
          0.1,
        );
        boat.rotation.x = Math.sin(elapsed * 2.25) * 0.035 + (boost ? -0.025 : 0);
        setSpeedLabel(boost ? "전속" : brake ? "감속" : "순항");

        if (elapsed - lastWake > (boost ? 0.045 : 0.075)) {
          lastWake = elapsed;
          clockPosition.set(
            boat.position.x + (Math.random() - 0.5) * 1.25,
            -0.2,
            boat.position.z + 2.5 + Math.random(),
          );
          spawnParticles(clockPosition, 0xd8fbff, boost ? 3 : 2, 0.55);
        }

        collectibles.forEach((item, index) => {
          if (item.collected) return;
          item.group.rotation.y += dt * 1.7;
          item.group.position.y = Math.sin(elapsed * 2.4 + index) * 0.25;
          const dx = item.group.position.x - boat.position.x;
          const dz = item.group.position.z - boat.position.z;
          if (dx * dx + dz * dz < 5.2) {
            item.collected = true;
            item.group.visible = false;
            comboRef.current += 1;
            collectedRef.current += 1;
            scoreRef.current += 100 + Math.min(comboRef.current, 5) * 20;
            setCombo(comboRef.current);
            setCollected(collectedRef.current);
            setScore(scoreRef.current);
            soundRef.current?.pickup(comboRef.current);
            spawnParticles(item.group.position.clone(), 0xffdc55, 18, 3.8);
            showToast(`${item.label} 인사이트 획득 · 콤보 ×${comboRef.current}`);
          }
        });

        obstacles.forEach((obstacle, index) => {
          obstacle.group.rotation.y += Math.sin(index) * dt * 0.06;
          if (now < obstacle.hitUntil) return;
          const dx = obstacle.group.position.x - boat.position.x;
          const dz = obstacle.group.position.z - boat.position.z;
          const hitRadius = obstacle.radius + 1.05;
          if (dx * dx + dz * dz < hitRadius * hitRadius) {
            obstacle.hitUntil = now + 1600;
            obstacle.group.visible = false;
            healthRef.current = Math.max(0, healthRef.current - 25);
            scoreRef.current = Math.max(0, scoreRef.current - 75);
            comboRef.current = 0;
            setHealth(healthRef.current);
            setScore(scoreRef.current);
            setCombo(0);
            lateralVelocity += dx > 0 ? -7 : 7;
            shake = 0.8;
            soundRef.current?.crash();
            spawnParticles(boat.position.clone(), 0xc7eff5, 26, 4.8);
            showToast("암초 충돌! 경제의 불확실성을 피하세요");
            if (healthRef.current <= 0) {
              updateMode("lost");
              showToast("박정호호가 항로를 잃었습니다");
            }
          }
        });

        const travel = Math.max(0, -boat.position.z);
        if (now - lastHudUpdate > 90) {
          lastHudUpdate = now;
          setProgress(Math.min(100, (travel / COURSE_LENGTH) * 100));
        }
        if (travel >= COURSE_LENGTH) {
          scoreRef.current += Math.round(healthRef.current * 8 + collectedRef.current * 25);
          setScore(scoreRef.current);
          setProgress(100);
          updateMode("won");
          soundRef.current?.finish();
          spawnParticles(new THREE.Vector3(0, 8, boat.position.z - 10), 0xffd452, 70, 7);
          showToast("지식의 등대 도착! 오늘의 경제 항해 성공");
        }
      } else {
        boat.position.y = 0.18 + Math.sin(elapsed * 2.1) * 0.14;
      }

      water.position.z = boat.position.z - 95;
      sky.position.z = boat.position.z;
      sunDisc.position.z = boat.position.z - 180;
      sun.position.z = boat.position.z + 20;

      const desiredCamera = new THREE.Vector3(
        boat.position.x * 0.52,
        7.7 + (playing && boost ? 0.7 : 0),
        boat.position.z + 13.2,
      );
      if (shake > 0) {
        desiredCamera.x += (Math.random() - 0.5) * shake;
        desiredCamera.y += (Math.random() - 0.5) * shake;
        shake = Math.max(0, shake - dt * 2.8);
      }
      camera.position.lerp(desiredCamera, 1 - Math.pow(0.001, dt));
      camera.lookAt(boat.position.x * 0.75, 0.5, boat.position.z - 13);

      const beacon = lighthouse.getObjectByName("beacon");
      if (beacon) beacon.rotation.x = elapsed * 0.45;
      clouds.forEach((cloud, index) => {
        cloud.position.x += Math.sin(elapsed * 0.12 + index) * dt * 0.24;
      });

      for (let i = particles.length - 1; i >= 0; i -= 1) {
        const particle = particles[i];
        particle.life -= dt;
        particle.velocity.y -= 2.1 * dt;
        particle.mesh.position.addScaledVector(particle.velocity, dt);
        const material = particle.mesh.material as THREE.MeshBasicMaterial;
        material.opacity = Math.max(0, particle.life / particle.maxLife);
        particle.mesh.scale.setScalar(0.6 + (1 - particle.life / particle.maxLife) * 1.5);
        if (particle.life <= 0) {
          scene.remove(particle.mesh);
          particle.mesh.geometry.dispose();
          material.dispose();
          particles.splice(i, 1);
        }
      }

      renderer.render(scene, camera);
    };

    requestAnimationFrame(animate);

    return () => {
      const frameId = Number(mount.dataset.frameId);
      if (frameId) cancelAnimationFrame(frameId);
      if (toastTimeout) window.clearTimeout(toastTimeout);
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("keyup", handleKeyUp);
      renderer.dispose();
      scene.traverse((object) => {
        if (object instanceof THREE.Mesh) {
          object.geometry?.dispose();
          const materials = Array.isArray(object.material)
            ? object.material
            : [object.material];
          materials.forEach((material) => material?.dispose());
        }
      });
      mount.removeChild(renderer.domElement);
      resetRef.current = null;
    };
  }, [togglePause, updateMode]);

  useEffect(() => {
    const sound = new SoundEngine();
    soundRef.current = sound;
    return () => sound.dispose();
  }, []);

  const stageLabel =
    progress < 25
      ? "경제의 출항"
      : progress < 50
        ? "변수의 해협"
        : progress < 75
          ? "인사이트 해류"
          : "지식의 등대";

  return (
    <main className="game-shell">
      <div ref={mountRef} className="game-canvas" aria-hidden="true" />
      <div className="sea-vignette" />

      <header className="hud-top">
        <div className="brand-lockup">
          <span className="brand-mark">손경제</span>
          <div>
            <p>손에 잡히는 경제</p>
            <strong>박정호호의 모험</strong>
          </div>
        </div>

        <div className="stage-pill" aria-live="polite">
          <span className="live-dot" />
          {stageLabel}
        </div>

        <div className="top-actions">
          <button
            className="icon-button"
            type="button"
            onClick={toggleSound}
            aria-label={soundOn ? "소리 끄기" : "소리 켜기"}
            title={soundOn ? "소리 끄기" : "소리 켜기"}
          >
            {soundOn ? "♪" : "×"}
          </button>
          <button
            className="pause-button"
            type="button"
            onClick={togglePause}
            disabled={mode !== "playing" && mode !== "paused"}
          >
            {mode === "paused" ? "계속" : "일시정지"}
          </button>
        </div>
      </header>

      {(mode === "playing" || mode === "paused") && (
        <>
          <aside className="mission-card">
            <span className="eyebrow">오늘의 항해 미션</span>
            <strong>지식의 등대를 찾아서</strong>
            <p>경제 암초를 피하고 핵심 인사이트를 모으세요.</p>
            <div className="mission-stat">
              <span>인사이트</span>
              <b>{collected} / 31</b>
            </div>
          </aside>

          <div className="toast-message" aria-live="polite">
            {toast}
          </div>

          <section className="hud-bottom" aria-label="항해 상태">
            <div className="status-cluster">
              <div className="stat-box score-box">
                <span>항해 점수</span>
                <strong>{score.toLocaleString("ko-KR")}</strong>
              </div>
              <div className="stat-box compact">
                <span>속도</span>
                <strong>{speedLabel}</strong>
              </div>
              {combo > 1 && (
                <div className="combo-badge">COMBO ×{combo}</div>
              )}
            </div>

            <div className="voyage-progress">
              <div className="progress-labels">
                <span>출항</span>
                <strong>{Math.round(progress)}%</strong>
                <span>지식의 등대</span>
              </div>
              <div className="progress-track">
                <div className="progress-fill" style={{ width: `${progress}%` }} />
                <div className="boat-pin" style={{ left: `${progress}%` }}>⛴</div>
              </div>
            </div>

            <div className="health-cluster">
              <div className="health-copy">
                <span>선체 내구도</span>
                <strong>{health}%</strong>
              </div>
              <div className="health-track">
                <div
                  className="health-fill"
                  style={{ width: `${health}%` }}
                  data-low={health <= 35}
                />
              </div>
            </div>
          </section>

          <div className="desktop-controls">
            <span><kbd>←</kbd><kbd>→</kbd> 방향</span>
            <span><kbd>↑</kbd> 전속</span>
            <span><kbd>↓</kbd> 감속</span>
            <span><kbd>P</kbd> 정지</span>
          </div>

          <div className="touch-controls" aria-label="모바일 조작 버튼">
            <div className="touch-steer">
              <button
                type="button"
                aria-label="왼쪽으로 이동"
                onPointerDown={() => setVirtualKey("arrowleft", true)}
                onPointerUp={() => setVirtualKey("arrowleft", false)}
                onPointerCancel={() => setVirtualKey("arrowleft", false)}
              >←</button>
              <button
                type="button"
                aria-label="오른쪽으로 이동"
                onPointerDown={() => setVirtualKey("arrowright", true)}
                onPointerUp={() => setVirtualKey("arrowright", false)}
                onPointerCancel={() => setVirtualKey("arrowright", false)}
              >→</button>
            </div>
            <button
              className="boost-control"
              type="button"
              onPointerDown={() => setVirtualKey("arrowup", true)}
              onPointerUp={() => setVirtualKey("arrowup", false)}
              onPointerCancel={() => setVirtualKey("arrowup", false)}
            >전속</button>
          </div>
        </>
      )}

      {mode === "intro" && (
        <section className="modal-layer intro-layer">
          <div className="intro-card">
            <div className="program-tag">3D ECONOMY VOYAGE</div>
            <p className="intro-kicker">거대한 경제의 바다가 열립니다</p>
            <h1>
              박정호호의
              <span>모험</span>
            </h1>
            <p className="intro-description">
              금리의 파도, 환율의 바람, 불확실성의 암초를 넘어<br />
              오늘의 경제를 밝혀줄 <b>지식의 등대</b>로 향하세요.
            </p>

            <div className="briefing-grid">
              <div><i>01</i><span>경제 암초를<br />피하세요</span></div>
              <div><i>02</i><span>핵심 인사이트를<br />모으세요</span></div>
              <div><i>03</i><span>지식의 등대에<br />도착하세요</span></div>
            </div>

            <button
              className="primary-button"
              type="button"
              onClick={startGame}
              disabled={webglUnavailable}
            >
              <span>박정호호 출항하기</span>
              <b>→</b>
            </button>
            <p className="start-hint">
              {webglUnavailable
                ? "3D 가속을 사용할 수 없습니다 · 브라우저의 하드웨어 가속을 켜주세요"
                : "방향키 또는 WASD · 소리를 켜고 플레이해 보세요"}
            </p>
          </div>
        </section>
      )}

      {mode === "paused" && (
        <section className="modal-layer compact-layer">
          <div className="result-card pause-card">
            <span className="result-icon">⚓</span>
            <p className="eyebrow">잠시 닻을 내렸습니다</p>
            <h2>항해 일시정지</h2>
            <p>경제의 흐름은 기다려주지 않지만,<br />잠깐 숨을 고르는 것도 전략입니다.</p>
            <button className="primary-button" type="button" onClick={togglePause}>
              항해 계속하기 <b>→</b>
            </button>
          </div>
        </section>
      )}

      {(mode === "won" || mode === "lost") && (
        <section className="modal-layer compact-layer">
          <div className={`result-card ${mode}`}>
            <span className="result-icon">{mode === "won" ? "✦" : "〰"}</span>
            <p className="eyebrow">
              {mode === "won" ? "TODAY'S VOYAGE COMPLETE" : "ROUTE LOST"}
            </p>
            <h2>{mode === "won" ? "지식의 등대 도착!" : "항로를 다시 계산합니다"}</h2>
            <p>
              {mode === "won"
                ? "불확실성의 바다를 건너 오늘의 경제에 한 걸음 더 가까워졌습니다."
                : "경제의 파도는 거칠었습니다. 인사이트를 모아 다시 도전해 보세요."}
            </p>
            <div className="result-score">
              <div><span>최종 점수</span><strong>{score.toLocaleString("ko-KR")}</strong></div>
              <div><span>획득 인사이트</span><strong>{collected}<small>/31</small></strong></div>
              <div><span>선체 내구도</span><strong>{health}<small>%</small></strong></div>
            </div>
            <button className="primary-button" type="button" onClick={startGame}>
              {mode === "won" ? "다시 항해하기" : "재도전하기"} <b>↻</b>
            </button>
          </div>
        </section>
      )}

      <footer className="broadcast-strip">
        <span>SONGYEONGJE</span>
        <p>손에 잡히는 경제 · 정보의 바다를 가장 쉽고 정확하게</p>
        <span>CAPTAIN PARK</span>
      </footer>
    </main>
  );
}
